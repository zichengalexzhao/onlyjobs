# backend/services/process_emails/main.py

import os
import json
import base64
from flask import Flask, request, jsonify
from datetime import datetime, date
from google.cloud import bigquery, firestore
import uuid

from classifier_logic import is_job_application, classify_email

PROJECT_ID = os.environ.get("PROJECT_ID", "your-gcp-project-id")
LOCATION = os.environ.get("LOCATION", "us-central1")
BQ_DATASET_ID = os.environ.get("BQ_DATASET_ID", "user_data")
BQ_RAW_TABLE_ID = os.environ.get("BQ_RAW_TABLE_ID", "job_applications")

# --- FIX APPLIED HERE for Firestore client initialization ---
# Define your named Firestore database ID
FIRESTORE_DATABASE_ID = os.environ.get("FIRESTORE_DATABASE_ID", "emails-firestore") # Make sure this matches the name in your Firebase console

bigquery_client = bigquery.Client(project=PROJECT_ID)
# Initialize Firestore client, explicitly providing the named database ID
firestore_client = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE_ID)

app = Flask(__name__)
app.debug = True
app.config["PROPAGATE_EXCEPTIONS"] = True

def normalize_status(raw_status):
    raw = raw_status.lower().strip()
    if any(word in raw for word in ["declined", "rejected", "not selected"]):
        return "Declined"
    elif any(word in raw for word in ["offer", "accepted"]):
        return "Offer"
    elif "interview" in raw:
        return "Interviewed"
    elif any(word in raw for word in ["applied", "submitted", "received"]):
        return "Applied"
    else:
        return "Applied"

def parse_classification_details(classification):
    details = {
        "Company": "",
        "Job Title": "",
        "Location": "",
        "status": "",
    }
    for line in classification.splitlines():
        line = line.strip()
        if line.lower().startswith("company:"):
            details["Company"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("job title:"):
            details["Job Title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("location:"):
            details["Location"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("status:"):
            raw_status = line.split(":", 1)[1].strip()
            details["status"] = normalize_status(raw_status)
    return details

def save_results_to_bigquery(rows):
    table_ref = bigquery_client.dataset(BQ_DATASET_ID).table(BQ_RAW_TABLE_ID)
    errors = bigquery_client.insert_rows_json(table_ref, rows)
    if errors:
        print("BigQuery insert errors:", errors)
    else:
        print(f"✅ Inserted {len(rows)} rows to BigQuery")

def save_results_to_firestore(data_dict, user_id, email_id):
    try:
        doc_ref = firestore_client.collection('users').document(user_id).collection('job_applications').document(email_id)
        doc_ref.set(data_dict)
        print(f"✅ Saved email {email_id} for user {user_id} to Firestore.")
    except Exception as e:
        print(f"❌ Error saving to Firestore for email {email_id}, user {user_id}: {e}")

@app.route('/', methods=['POST'])
def index():
    envelope = request.get_json()
    if not envelope:
        print("No Pub/Sub message received.")
        return 'No Pub/Sub message received', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        print("Invalid Pub/Sub message format. Missing 'message' field.")
        return 'Invalid Pub/Sub message format', 400

    message = envelope['message']
    
    if 'data' not in message:
        print("No 'data' field in Pub/Sub message.")
        return 'No data in message', 400

    pubsub_data = base64.b64decode(message['data']).decode('utf-8')

    try:
        email_payload = json.loads(pubsub_data)
        email_content = email_payload.get('email_content')
        user_id = email_payload.get('user_id')
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON payload: {e}")
        print(f"Raw Pub/Sub data: {pubsub_data}")
        return 'Invalid JSON payload', 400

    if not email_content or not user_id:
        print(f"Missing email_content or user_id in payload. User: {user_id}, Content length: {len(email_content) if email_content else 0}")
        return 'Missing email_content or user_id', 400

    email_id = email_payload.get('email_id', f"local-{uuid.uuid4()}")

    print(f"Processing email for user: {user_id}, ID: {email_id}")

    classification_result = classify_email(email_content)

    if "not job application" in classification_result.lower():
        print(f"Email {email_id} for user {user_id} skipped (classified as not job-related).")
        return 'Email classified as not job application', 200

    details = parse_classification_details(classification_result)
    
    # Add common metadata
    details["email_id"] = email_id
    details["user_id"] = user_id
    details["inserted_at"] = datetime.utcnow().isoformat()
    
    details["email_date"] = email_payload.get("email_date", date.today().isoformat())


    # 4. Save to BigQuery
    bq_row = {
        "user_id": details.get("user_id"),
        "email_id": details.get("email_id"),
        "company": details.get("Company"),
        "job_title": details.get("Job Title"),
        "location": details.get("Location"),
        "status": details.get("status"),
        "inserted_at": details.get("inserted_at"),
        "email_date": details.get("email_date"),
        "raw_email_content": email_content
    }
    save_results_to_bigquery([bq_row])

    # 5. Save to Firestore
    firestore_data = {
        "company": details.get("Company"),
        "job_title": details.get("Job Title"),
        "location": details.get("Location"),
        "status": details.get("status"),
        "inserted_at": details.get("inserted_at"),
        "email_date": details.get("email_date"),
        "raw_email_content_snippet": email_content[:500]
    }
    save_results_to_firestore(firestore_data, user_id, email_id)

    return 'Email processed successfully', 200

if __name__ == '__main__':
    print("Running Cloud Run service locally. Expecting POST requests.")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))