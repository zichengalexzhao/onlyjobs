#manage_tokens
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
            error = request.args.get("error")
            state = request.args.get("state")
            
            if error:
                print(f"❌ OAuth error: {error}")
                frontend_url = get_secret("FRONTEND_REDIRECT_URL") if os.getenv("FRONTEND_REDIRECT_URL") else "http://localhost:3000/callback"
                return f'<script>window.location.href="{frontend_url}?error={error}";</script>', 400
            
            if not code:
                print("❌ No authorization code in redirect")
                frontend_url = get_secret("FRONTEND_REDIRECT_URL") if os.getenv("FRONTEND_REDIRECT_URL") else "http://localhost:3000/callback"
                return f'<script>window.location.href="{frontend_url}?error=missing_code";</script>', 400
            
            print(f"🔑 Authorization code received: {code}")
            
            # Extract UID from state parameter (we'll need to modify auth URL generation to include this)
            # For now, we'll need a different approach since we don't have the UID
            # Let's redirect to frontend with a special token that frontend can use
            
            try:
                # Exchange code for tokens immediately
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
                
                # We need the UID to store tokens, but we don't have it in the callback
                # Let's create a temporary token storage and redirect to frontend with a temp ID
                import uuid
                temp_id = str(uuid.uuid4())
                
                # Store tokens temporarily with temp_id (expires in 30 minutes)
                import datetime
                expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                
                firestore_client.collection("temp-tokens").document(temp_id).set({
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "expires_at": expiry_time
                })
                print(f"📦 Tokens stored temporarily with ID: {temp_id}")
                
                # Redirect to frontend with temp_id
                frontend_url = get_secret("FRONTEND_REDIRECT_URL") if os.getenv("FRONTEND_REDIRECT_URL") else "http://localhost:3000/callback"
                redirect_url = f"{frontend_url}?temp_token_id={temp_id}&status=success"
                print(f"🔀 Redirecting to frontend: {redirect_url}")
                return f'<script>window.location.href="{redirect_url}";</script>', 200
                
            except Exception as e:
                print(f"❌ Error exchanging code for tokens: {str(e)}")
                frontend_url = get_secret("FRONTEND_REDIRECT_URL") if os.getenv("FRONTEND_REDIRECT_URL") else "http://localhost:3000/callback"
                return f'<script>window.location.href="{frontend_url}?error={str(e)}";</script>', 500

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
        firestore_client.collection("gmail_auth").document(uid).set({
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

@app.route("/api/gmail/finalize-tokens", methods=["POST"])
def finalize_tokens():
    try:
        get_firebase_app()
        uid = verify_firebase_token(request)
        temp_token_id = request.json.get("temp_token_id")
        
        if not temp_token_id:
            return jsonify({"error": "Missing temp_token_id"}), 400
        
        # Get tokens from temporary storage
        temp_doc = firestore_client.collection("temp-tokens").document(temp_token_id).get()
        if not temp_doc.exists:
            print(f"❌ Temporary tokens not found for ID: {temp_token_id}")
            return jsonify({"error": "Temporary tokens not found or expired"}), 404
        
        temp_data = temp_doc.to_dict()
        
        # Check if tokens have expired
        import datetime
        if "expires_at" in temp_data:
            expires_at = temp_data["expires_at"]
            # Convert Firestore timestamp to datetime if needed
            if hasattr(expires_at, 'timestamp'):
                expires_at = expires_at.replace(tzinfo=None)  # Make timezone naive
            current_time = datetime.datetime.utcnow()
            if current_time > expires_at:
                print(f"❌ Temporary tokens expired for ID: {temp_token_id}")
                # Clean up expired tokens
                firestore_client.collection("temp-tokens").document(temp_token_id).delete()
                return jsonify({"error": "Temporary tokens have expired. Please try connecting again."}), 410
        
        print(f"✅ Temporary tokens found and valid for ID: {temp_token_id}")
        
        # Move tokens to permanent storage
        firestore_client.collection("gmail_auth").document(uid).set({
            "token": temp_data["token"],
            "refresh_token": temp_data["refresh_token"],
            "token_uri": temp_data["token_uri"],
            "client_id": temp_data["client_id"],
            "client_secret": temp_data["client_secret"],
            "scopes": temp_data["scopes"],
        })
        
        # Delete temporary tokens
        firestore_client.collection("temp-tokens").document(temp_token_id).delete()
        
        print(f"📬 Tokens finalized and stored in Firestore for {uid}")
        return jsonify({"status": "success"})
        
    except Exception as e:
        print(f"❌ Error in /finalize-tokens: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/gmail/status", methods=["GET"])
def gmail_status():
    try:
        get_firebase_app()
        uid = verify_firebase_token(request)
        
        # Check if user has tokens stored
        doc = firestore_client.collection("gmail_auth").document(uid).get()
        if doc.exists:
            # Try to get user email from tokens (basic validation)
            return jsonify({"connected": True})
        else:
            return jsonify({"connected": False})
            
    except Exception as e:
        print(f"❌ Error in /gmail/status: {str(e)}")
        return jsonify({"connected": False})

@app.route("/api/gmail/disconnect", methods=["DELETE"])
def disconnect():
    try:
        get_firebase_app()
        uid = verify_firebase_token(request)
        
        # Delete permanent tokens
        firestore_client.collection("gmail_auth").document(uid).delete()
        
        # Clean up any temporary tokens that might exist for this user
        # Note: This is a cleanup measure, though temp tokens aren't tied to UID
        temp_tokens = firestore_client.collection("temp-tokens").get()
        for doc in temp_tokens:
            try:
                # Delete old temporary tokens (older than 1 hour as cleanup)
                import datetime
                doc_data = doc.to_dict()
                if "created_at" in doc_data:
                    created_at = doc_data["created_at"]
                    if hasattr(created_at, 'timestamp'):
                        created_at = created_at.replace(tzinfo=None)
                    current_time = datetime.datetime.utcnow()
                    if current_time - created_at > datetime.timedelta(hours=1):
                        firestore_client.collection("temp-tokens").document(doc.id).delete()
                        print(f"🧹 Cleaned up old temporary token: {doc.id}")
            except Exception as cleanup_error:
                print(f"⚠️ Error cleaning temp token {doc.id}: {cleanup_error}")
        
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