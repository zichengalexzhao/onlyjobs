import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import secretmanager_v1, firestore
from google_auth_oauthlib.flow import Flow

# === Flask App Setup ===
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

firebase_app = None
firestore_client = firestore.Client()

# === Lazy Firebase Admin Init ===
def get_firebase_app():
    global firebase_app
    if firebase_app:
        return firebase_app
    print("🔑 Initializing Firebase Admin...")
    try:
        project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
        secret_name = "firebase-service-account"
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        client = secretmanager_v1.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": name})
        service_account_info = json.loads(response.payload.data.decode("UTF-8"))
        print(f"✅ Service account info: {service_account_info.get('project_id')}")
        cred = credentials.Certificate(service_account_info)
        firebase_app = firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin initialized.")
        return firebase_app
    except Exception as e:
        print(f"❌ Firebase initialization error: {str(e)}")
        raise

# === Fetch Secrets from Secret Manager ===
def get_secret(secret_name):
    client = secretmanager_v1.SecretManagerServiceClient()
    name = f"projects/{os.getenv('GCP_PROJECT')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# === Config ===
CLIENT_ID = get_secret("GOOGLE_OAUTH_CLIENT_ID")
CLIENT_SECRET = get_secret("GOOGLE_OAUTH_CLIENT_SECRET")
REDIRECT_URI = get_secret("GOOGLE_OAUTH_REDIRECT_URI")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

# === Token Verifier ===
def verify_firebase_token(request):
    print("🧪 Verifying Firebase token...")
    auth_header = request.headers.get("Authorization")
    print(f"🔍 Authorization header: {auth_header}")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("❌ Missing or malformed Authorization header")
    id_token = auth_header.split(" ")[1].encode('utf-8').decode('utf-8')  # Ensure UTF-8 handling
    print(f"🔍 Extracted ID token: {id_token[:50]}...")  # Log first 50 chars
    try:
        decoded_token = auth.verify_id_token(id_token)
        print(f"✅ Firebase UID: {decoded_token['uid']}, Exp: {decoded_token['exp']}")
        return decoded_token["uid"]
    except Exception as e:
        print(f"❌ Firebase ID token verification failed: {str(e)}")
        raise

# === Routes ===
@app.route("/api/debug", methods=["GET"])
def debug():
    print("📡 Debug endpoint hit")
    return jsonify({"status": "alive", "message": "Container is running"}), 200

@app.route("/api/gmail/auth-url", methods=["POST"])
def get_auth_url():
    try:
        get_firebase_app()
        uid = verify_firebase_token(request)

        flow = Flow.from_client_config({
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")

        print(f"🔗 Auth URL generated for {uid}")
        return jsonify({"authUrl": auth_url})
    except Exception as e:
        print("❌ Error in /auth-url:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/api/gmail/callback", methods=["GET", "POST"])
def callback():
    try:
        # For GET request from OAuth redirect, no Firebase token required
        if request.method == "GET":
            code = request.args.get("code")
            if not code:
                return jsonify({"error": "Missing auth code in redirect"}), 400
            print(f"🔑 Authorization code received: {code}")
            return jsonify({"code": code, "status": "received"}), 200  # Return code for manual use

        # For POST request (e.g., manual testing with code), require Firebase token
        get_firebase_app()  # Ensure Firebase is initialized
        uid = verify_firebase_token(request)
        code = request.json.get("code")
        if not code:
            return jsonify({"error": "Missing auth code"}), 400

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Store tokens in Firestore
        firestore_client.collection("emails-firestore").document(uid).set({
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        })
        print(f"📬 Tokens stored in Firestore for {uid}")
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"❌ Error in /callback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/gmail/disconnect", methods=["POST"])
def disconnect():
    try:
        get_firebase_app()
        uid = verify_firebase_token(request)
        firestore_client.collection("emails-firestore").document(uid).delete()
        print(f"🔌 Disconnected Gmail for {uid}")
        return jsonify({"status": "disconnected"})
    except Exception as e:
        print("❌ Error in /disconnect:", str(e))
        return jsonify({"error": str(e)}), 500

# === CORS Preflight ===
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# === Main ===
if __name__ == "__main__":
    print("🚀 Starting manage-tokens app...")
    app.run(debug=True, host="0.0.0.0", port=8080)