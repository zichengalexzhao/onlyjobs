# === manage_tokens/main.py ===
import os
import json
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import firebase_admin
from firebase_admin import auth, credentials, initialize_app
from google.cloud import secretmanager_v1
from google.auth.transport import requests as grequests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.cloud import firestore

# === App Setup ===
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# === Load Firebase Admin Credentials from Secret Manager ===
def initialize_firebase():
    project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
    secret_name = "firebase-service-account"

    client = secretmanager_v1.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    service_account_info = json.loads(response.payload.data.decode("UTF-8"))

    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

initialize_firebase()

# === OAuth2 Config ===
CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

firestore_client = firestore.Client()

# === Helpers ===
def verify_firebase_token(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("Missing or malformed Authorization header")
    id_token = auth_header.split(" ")[1]
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token["uid"]

# === Routes ===
@app.route("/api/gmail/auth-url", methods=["POST"])
def get_auth_url():
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
    return jsonify({"authUrl": auth_url})

@app.route("/api/gmail/callback", methods=["POST"])
def callback():
    uid = verify_firebase_token(request)
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "Missing auth code"}), 400

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
    flow.fetch_token(code=code)
    creds = flow.credentials

    firestore_client.collection("emails-firestore").document(uid).set({
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    })
    return jsonify({"status": "success"})

@app.route("/api/gmail/disconnect", methods=["POST"])
def disconnect():
    uid = verify_firebase_token(request)
    firestore_client.collection("emails-firestore").document(uid).delete()
    return jsonify({"status": "disconnected"})

# === CORS Preflight ===
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# === Main Entry ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)