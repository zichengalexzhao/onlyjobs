# gmail_fetch/main.py

import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore
from google.cloud.pubsub_v1 import PublisherClient
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
import requests

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://onlyjobs-465420.web.app",
    "https://onlyjobs-465420.firebaseapp.com",
])

print("🚀 Starting gmail-fetch app…")

PROJECT_ID            = "onlyjobs-465420"
FIRESTORE_COLLECTION  = "gmail_auth"
PUBSUB_TOPIC          = f"projects/{PROJECT_ID}/topics/new-emails-topic"

# === Initialize Clients ===
firestore_client = firestore.Client(project=PROJECT_ID)
publisher        = PublisherClient()


def fetch_emails_for_user(uid, creds_dict, backfill=False, max_emails=500):
    print(f"📩 Fetching emails for user: {uid}")

    # build Credentials and refresh to get a valid access token
    creds = Credentials(
        token=creds_dict.get("token"),
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
        scopes=creds_dict.get("scopes", []),
    )
    creds.refresh(google.auth.transport.requests.Request())

    headers = {"Authorization": f"Bearer {creds.token}"}
    list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    # figure out how far we’ve already fetched
    last_fetched_ms = creds_dict.get("last_fetched", 0)
    after_secs      = int(last_fetched_ms / 1000)

    fetched = 0
    next_page_token = None

    while True:
        params = {
            "maxResults": 100 if backfill else 10,
            "labelIds": ["INBOX"],
        }
        # only pull messages *after* our last fetch (unless backfill)
        if not backfill and after_secs:
            params["q"] = f"after:{after_secs}"

        if next_page_token:
            params["pageToken"] = next_page_token

        resp = requests.get(list_url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        msgs = data.get("messages", [])
        next_page_token = data.get("nextPageToken")
        print(f"📬 Retrieved {len(msgs)} messages")

        if not msgs:
            break

        for m in msgs:
            msg_id = m["id"]
            detail_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
            dresp = requests.get(detail_url, headers=headers)
            dresp.raise_for_status()
            payload = dresp.json()

            email_date = int(payload.get("internalDate", 0))
            snippet    = payload.get("snippet", "")

            pubsub_data = json.dumps({
                "user_id":       uid,
                "email_id":      msg_id,
                "email_content": snippet,
                "email_date":    email_date,
            }).encode("utf-8")

            publisher.publish(PUBSUB_TOPIC, data=pubsub_data).result()
            print(f"✅ Published email {msg_id}")

            fetched += 1
            time.sleep(0.1)
            if not backfill and fetched >= max_emails:
                break

        if not backfill or not next_page_token or fetched >= max_emails:
            break

    # update last_fetched so next run only gets newer messages
    firestore_client.collection(FIRESTORE_COLLECTION).document(uid).update({
        "last_fetched": int(time.time() * 1000)
    })
    print(f"🔄 Updated last_fetched for {uid}")

    return fetched


@app.route("/fetch", methods=["POST"])
def fetch_all():
    print("📥 Received /fetch POST request")
    backfill = request.args.get("backfill", "false").lower() == "true"
    explicit_uid = request.args.get("uid")

    # choose which user docs to process
    if explicit_uid:
        docs = [firestore_client.collection(FIRESTORE_COLLECTION).document(explicit_uid).get()]
    else:
        docs = firestore_client.collection(FIRESTORE_COLLECTION).stream()

    processed_users = 0
    for doc in docs:
        if not doc.exists:
            print(f"⚠️ No creds found for UID={doc.id}")
            continue

        creds = doc.to_dict()
        if "token" not in creds:
            print(f"⚠️ Skipping {doc.id} — no token field")
            continue

        try:
            fetched = fetch_emails_for_user(doc.id, creds, backfill=backfill)
            if fetched:
                processed_users += 1
        except Exception as e:
            print(f"❌ Error for {doc.id}: {e}")

    print(f"✅ Done. Processed {processed_users} user(s).")
    return jsonify({
        "status":          "complete",
        "users_processed": processed_users,
        "backfill":        backfill
    })


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
