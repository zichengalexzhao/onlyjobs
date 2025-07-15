import os
import functions_framework
import google.oauth2.credentials
from google.cloud import secretmanager_v1
from google.cloud import firestore
from google.auth.transport import requests
from google.oauth2 import id_token
import json
import logging # Added for better logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Cloud clients
secret_manager_client = secretmanager_v1.SecretManagerServiceClient()
firestore_client = firestore.Client()

# Environment variables for OAuth credentials (configured during deployment)
# Get these from your GCP OAuth Client ID (Web application)
CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

# This REDIRECT_URI must match one of the 'Authorized redirect URIs' in your GCP OAuth Client ID.
# It's the URL Google redirects to after user consent. For local testing, this will be your frontend's localhost URL.
REDIRECT_URI = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')

PROJECT_ID = os.environ.get('GCP_PROJECT') # Automatically provided by Cloud Functions

@functions_framework.http
def manage_tokens(request):
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*', # **IMPORTANT**: In production, replace '*' with your frontend's domain (e.g., 'https://app.onlyjobs.com')
            'Access-Control-Allow-Methods': 'POST, GET, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for actual requests
    headers = {
        'Access-Control-Allow-Origin': '*' # **IMPORTANT**: In production, replace '*' with your frontend's domain
    }

    # --- Endpoint: GET /api/gmail/auth-url ---
    if request.path == '/api/gmail/auth-url' and request.method == 'GET':
        if not CLIENT_ID or not REDIRECT_URI:
            logger.error("Missing CLIENT_ID or REDIRECT_URI environment variables.")
            return ('Server configuration error: Missing OAuth credentials.', 500, headers)

        # Define Gmail scopes needed for fetching emails
        # These must match the scopes you configured in your GCP OAuth Consent Screen
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]

        # Generate the Google OAuth authorization URL
        # access_type=offline is CRITICAL for getting a refresh token
        # prompt=consent is good for testing to ensure you always get a new refresh token
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={CLIENT_ID}&"
            f"redirect_uri={REDIRECT_URI}&"
            f"scope={'+'.join(scopes)}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        logger.info(f"Generated OAuth URL for frontend: {auth_url[:100]}...") # Log partial URL
        return json.dumps({'authUrl': auth_url}), 200, headers # Use json.dumps for jsonify equivalent

    # --- Endpoint: POST /api/gmail/callback ---
    elif request.path == '/api/gmail/callback' and request.method == 'POST':
        # 1. Authenticate user with Firebase ID Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return ('Unauthorized: Missing or invalid Authorization header.', 401, headers)

        firebase_id_token = auth_header.split(' ')[1]
        try:
            # Verify the Firebase ID token to get the user's UID
            # audience=PROJECT_ID ensures the token is for this project
            claims = id_token.verify_firebase_token(firebase_id_token, requests.Request(), audience=PROJECT_ID)
            user_uid = claims['uid']
            user_email = claims.get('email') # Get email from Firebase claims
            logger.info(f"Authenticated user for callback: {user_uid}, email: {user_email}")
        except ValueError as e:
            logger.error(f"Firebase ID token verification failed: {e}")
            return ('Unauthorized: Invalid Firebase ID token.', 401, headers)

        # 2. Extract authorization code from request body
        request_json = request.get_json(silent=True)
        if not request_json or 'code' not in request_json:
            return ('Bad Request: Missing authorization code.', 400, headers)
        auth_code = request_json['code']
        logger.info(f"Received authorization code for user {user_uid}.")

        # 3. Exchange authorization code for refresh token
        if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
            logger.error("Server configuration error: Missing OAuth client credentials or redirect URI.")
            return ('Server configuration error.', 500, headers)

        try:
            # Use google.oauth2.credentials to exchange the code
            credentials = google.oauth2.credentials.Credentials.from_authorization_code(
                auth_code,
                redirect_uri=REDIRECT_URI,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri='https://oauth2.googleapis.com/token'
            )
            refresh_token = credentials.refresh_token

            if not refresh_token:
                logger.warning(f"Failed to get a refresh token for {user_uid}. Ensure 'access_type=offline' and 'prompt=consent' were used in OAuth URL.")
                return ('Failed to obtain refresh token. User might not have granted offline access.', 400, headers)

            logger.info(f"Obtained refresh token for {user_uid}")

        except Exception as e:
            logger.error(f"Error exchanging authorization code for {user_uid}: {e}")
            return (f'Error exchanging code: {str(e)}', 500, headers)

        # 4. Store Refresh Token in Secret Manager
        # Each user's refresh token gets its own secret
        secret_id = f'gmail-refresh-token-{user_uid}'
        secret_path = f"projects/{PROJECT_ID}/secrets/{secret_id}"

        try:
            # Check if secret exists; if so, add a new version. Otherwise, create it.
            try:
                # Try to get the secret, if it exists, add a new version
                secret_manager_client.get_secret(name=secret_path)
                logger.info(f"Secret '{secret_id}' already exists. Adding new version.")
                payload_bytes = refresh_token.encode('UTF-8')
                secret_manager_client.add_secret_version(
                    request={"parent": secret_path, "payload": {"data": payload_bytes}}
                )
            except Exception as e: # Likely NotFound if secret doesn't exist
                logger.info(f"Secret '{secret_id}' not found. Creating new secret. Error: {e}")
                secret_manager_client.create_secret(
                    request={
                        "parent": f"projects/{PROJECT_ID}",
                        "secret_id": secret_id,
                        "secret": {"replication": {"automatic": {}}},
                    }
                )
                payload_bytes = refresh_token.encode('UTF-8')
                secret_manager_client.add_secret_version(
                    request={"parent": secret_path, "payload": {"data": payload_bytes}}
                )
            logger.info(f"Refresh token for {user_uid} stored in Secret Manager: {secret_id}")

        except Exception as e:
            logger.error(f"Error storing refresh token in Secret Manager for {user_uid}: {e}")
            return (f'Error storing token: {str(e)}', 500, headers)

        # 5. Store Basic Mapping in Firestore
        try:
            user_ref = firestore_client.collection('users').document(user_uid)
            user_ref.set({
                'gmail_email': user_email, # From Firebase ID token
                'gmail_access_granted': True,
                'last_gmail_fetch': firestore.SERVER_TIMESTAMP # Current timestamp on server
            }, merge=True)
            logger.info(f"Firestore mapping for {user_uid} updated.")
        except Exception as e:
            logger.error(f"Error storing Firestore mapping for {user_uid}: {e}")
            # This is not a critical failure for the OAuth flow, but should be logged.
            pass

        return ('Tokens managed successfully', 200, headers)

    # --- Endpoint: DELETE /api/gmail/disconnect ---
    elif request.path == '/api/gmail/disconnect' and request.method == 'DELETE':
        # 1. Authenticate user with Firebase ID Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return ('Unauthorized: Missing or invalid Authorization header.', 401, headers)

        firebase_id_token = auth_header.split(' ')[1]
        try:
            claims = id_token.verify_firebase_token(firebase_id_token, requests.Request(), audience=PROJECT_ID)
            user_uid = claims['uid']
            logger.info(f"Authenticated user for disconnect: {user_uid}")
        except ValueError as e:
            logger.error(f"Firebase ID token verification failed: {e}")
            return ('Unauthorized: Invalid Firebase ID token.', 401, headers)

        # 2. Delete Refresh Token from Secret Manager
        secret_id = f'gmail-refresh-token-{user_uid}'
        secret_path = f"projects/{PROJECT_ID}/secrets/{secret_id}"

        try:
            # Destroy all versions of the secret (effectively deleting it)
            secret_manager_client.delete_secret(name=secret_path)
            logger.info(f"Secret '{secret_id}' deleted from Secret Manager.")
        except Exception as e:
            logger.warning(f"Could not delete secret '{secret_id}' for {user_uid}: {e}")
            # If secret doesn't exist, that's fine, just log a warning.

        # 3. Update Firestore mapping
        try:
            user_ref = firestore_client.collection('users').document(user_uid)
            user_ref.update({
                'gmail_access_granted': False,
                'last_gmail_fetch': None # Clear last fetch timestamp
            })
            logger.info(f"Firestore mapping for {user_uid} updated to disconnected.")
        except Exception as e:
            logger.error(f"Error updating Firestore mapping for {user_uid} on disconnect: {e}")
            pass

        return ('Gmail disconnected successfully', 200, headers)

    # --- Other Endpoints (Placeholder for future API layer) ---
    # Your frontend expects:
    # POST /api/users
    # GET /api/users/me
    # PUT /api/users/me
    # POST /api/sync/trigger
    # GET /api/sync/status
    # GET /api/applications
    # GET /api/applications/stats

    return ('Not Found or Invalid Method', 404, headers) # Default for unhandled paths