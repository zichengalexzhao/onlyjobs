#gmail_fetch/main.py

import os
import json
import time
from flask import Flask, request, jsonify
from google.cloud import firestore, pubsub_v1
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
import requests
from google.cloud.pubsub_v1 import PublisherClient

app = Flask(__name__)
print("🚀 Starting gmail-fetch app...")

PROJECT_ID = "onlyjobs-465420"
FIRESTORE_COLLECTION = "gmail_auth"
PUBSUB_TOPIC = f"projects/{PROJECT_ID}/topics/new-emails-topic"

# === Initialize Clients ===
try:
    firestore_client = firestore.Client(project=PROJECT_ID)
    print("✅ Firestore client initialized")
except Exception as e:
    print(f"❌ Firestore client failed to init: {e}")
    raise

try:
    publisher = PublisherClient()
    print("✅ Pub/Sub publisher initialized")
except Exception as e:
    print(f"❌ Pub/Sub publisher failed to init: {e}")
    raise

# === Fetch Emails for One User ===
def fetch_emails_for_user(uid, creds_dict, backfill=False, max_emails=500):
    print(f"📩 Fetching emails for user: {uid}")

    try:
        creds = Credentials(
            token=creds_dict["token"],
            refresh_token=creds_dict["refresh_token"],
            token_uri=creds_dict["token_uri"],
            client_id=creds_dict["client_id"],
            client_secret=creds_dict["client_secret"],
            scopes=creds_dict["scopes"]
        )
        creds.refresh(google.auth.transport.requests.Request())
    except Exception as e:
        print(f"❌ Credential error for {uid}: {e}")
        return

    headers = {"Authorization": f"Bearer {creds.token}"}
    list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    fetched = 0
    next_page_token = None

    while True:
        try:
            params = {"maxResults": 100 if backfill else 10, "labelIds": ["INBOX"]}
            if backfill and next_page_token:
                params["pageToken"] = next_page_token

            res = requests.get(list_url, headers=headers, params=params)
            res.raise_for_status()
            response_json = res.json()

            messages = response_json.get("messages", [])
            next_page_token = response_json.get("nextPageToken")
            print(f"📬 Retrieved {len(messages)} messages")

            if not messages:
                break

            for msg in messages:
                try:
                    msg_id = msg["id"]
                    detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
                    msg_res = requests.get(detail_url, headers=headers)
                    msg_res.raise_for_status()
                    payload = msg_res.json()

                    email_date = int(payload.get("internalDate", "0"))
                    snippet = payload.get("snippet", "")

                    pubsub_data = json.dumps({
                        "user_id": uid,
                        "email_id": msg_id,
                        "email_content": snippet,
                        "email_date": email_date
                    }).encode("utf-8")

                    future = publisher.publish(PUBSUB_TOPIC, data=pubsub_data)
                    future.result()
                    print(f"✅ Published email {msg_id}")
                    fetched += 1

                    time.sleep(0.2)

                    if not backfill and fetched >= max_emails:
                        break

                except Exception as msg_err:
                    print(f"⚠️ Error processing message {msg.get('id')}: {msg_err}")
                    continue

            if not backfill or not next_page_token or fetched >= max_emails:
                break

        except Exception as page_err:
            print(f"❌ Error fetching email list: {page_err}")
            break

    try:
        firestore_client.collection(FIRESTORE_COLLECTION).document(uid).update({
            "last_fetched": int(time.time() * 1000)
        })
    except Exception as update_err:
        print(f"⚠️ Failed to update last_fetched for {uid}: {update_err}")

# === Cloud Function Route ===
@app.route("/fetch", methods=["POST"])
def fetch_all():
    print("📥 Received /fetch POST request")
    backfill = request.args.get("backfill", "false").lower() == "true"
    print(f"🛠 Backfill mode: {backfill}")

    try:
        users = firestore_client.collection(FIRESTORE_COLLECTION).stream()
    except Exception as stream_err:
        print(f"❌ Failed to stream Firestore users: {stream_err}")
        return jsonify({"status": "error", "message": str(stream_err)}), 500

    count = 0
    for doc in users:
        uid = doc.id
        creds_dict = doc.to_dict()

        if "token" not in creds_dict:
            print(f"⚠️ Skipping {uid} — no token found")
            continue

        try:
            fetch_emails_for_user(uid, creds_dict, backfill=backfill)
            count += 1
        except Exception as user_err:
            print(f"❌ Error fetching for {uid}: {user_err}")

    print(f"✅ All done. Processed {count} user(s).")
    return jsonify({"status": "complete", "users_processed": count, "backfill": backfill})

# === Health Check ===
@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# === Local Run ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
