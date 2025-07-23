# === gmail_fetch/main.py ===
import os
import json
from flask import Flask, request, jsonify
from google.cloud import firestore, pubsub_v1
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
import base64
import requests

app = Flask(__name__)

PROJECT_ID = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
FIRESTORE_COLLECTION = "emails-firestore"
PUBSUB_TOPIC = f"projects/{PROJECT_ID}/topics/new-emails-topic"

firestore_client = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()

# === Helper: Get Gmail messages ===
def fetch_emails_for_user(uid, creds_dict):
    creds = Credentials(
        token=creds_dict["token"],
        refresh_token=creds_dict["refresh_token"],
        token_uri=creds_dict["token_uri"],
        client_id=creds_dict["client_id"],
        client_secret=creds_dict["client_secret"],
        scopes=creds_dict["scopes"]
    )
    creds.refresh(google.auth.transport.requests.Request())

    headers = {"Authorization": f"Bearer {creds.token}"}
    list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": 10, "labelIds": ["INBOX"]}
    res = requests.get(list_url, headers=headers, params=params)
    res.raise_for_status()
    messages = res.json().get("messages", [])

    for msg in messages:
        msg_id = msg["id"]
        detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
        msg_res = requests.get(detail_url, headers=headers)
        msg_res.raise_for_status()
        payload = msg_res.json()

        snippet = payload.get("snippet", "")
        email_date = payload.get("internalDate")

        pubsub_data = json.dumps({
            "user_id": uid,
            "email_id": msg_id,
            "email_content": snippet,
            "email_date": email_date
        }).encode("utf-8")

        publisher.publish(PUBSUB_TOPIC, data=pubsub_data)
        print(f"✅ Published email {msg_id} for user {uid}")

# === Cloud Function Entry Point ===
@app.route("/fetch", methods=["POST"])
def fetch_all():
    users = firestore_client.collection(FIRESTORE_COLLECTION).stream()
    count = 0
    for doc in users:
        uid = doc.id
        creds_dict = doc.to_dict()
        try:
            fetch_emails_for_user(uid, creds_dict)
            count += 1
        except Exception as e:
            print(f"❌ Failed to fetch for {uid}: {e}")
    return jsonify({"status": "complete", "users_processed": count})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)