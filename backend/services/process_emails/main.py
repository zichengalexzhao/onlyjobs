# process_emails/main.py

import os
import json
import base64
import uuid
from datetime import datetime
from flask import Flask, request
from google.cloud import bigquery, firestore, pubsub_v1
from google.cloud.exceptions import NotFound

from config import PROJECT_ID, LOCATION
from classifier_logic import is_job_application, classify_email

def get_env(var_name, default_value):
    val = os.environ.get(var_name, default_value)
    print(f"[DEBUG] ENV {var_name} = {val}")
    return val

PROJECT_ID         = get_env("PROJECT_ID",         "onlyjobs-465420")
LOCATION           = get_env("LOCATION",           "us")            # BigQuery wants a multi-region like "US"
BQ_DATASET_ID      = get_env("BQ_DATASET_ID",      "user_data")
BQ_RAW_TABLE_ID    = get_env("BQ_RAW_TABLE_ID",    "job_applications")
FIRESTORE_DB_ID    = get_env("FIRESTORE_DATABASE_ID", "emails-firestore")
PUBSUB_TOPIC       = get_env("PUBSUB_TOPIC",       "applications-ready-topic")

print(f"[DEBUG] Initializing BigQuery client for project: {PROJECT_ID}")
bigquery_client = bigquery.Client(project=PROJECT_ID)

print(f"[DEBUG] Initializing Firestore client for project: {PROJECT_ID}, database: {FIRESTORE_DB_ID}")
firestore_client = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DB_ID)

print(f"[DEBUG] Initializing Pub/Sub publisher for topic: {PUBSUB_TOPIC}")
publisher    = pubsub_v1.PublisherClient()
topic_path   = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)

app = Flask(__name__)
app.debug = True
app.config["PROPAGATE_EXCEPTIONS"] = True

def normalize_status(raw_status):
    raw = raw_status.lower().strip()
    if any(w in raw for w in ["declined", "rejected", "not selected"]):
        return "Declined"
    if any(w in raw for w in ["offer", "accepted"]):
        return "Offer"
    if "interview" in raw:
        return "Interviewed"
    return "Applied"

def parse_classification_details(classification):
    print(f"[DEBUG] Raw classification result:\n{classification}")
    details = {"Company": "", "Job Title": "", "Location": "", "status": ""}
    for line in classification.splitlines():
        line = line.strip()
        if line.lower().startswith("company:"):
            details["Company"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("job title:"):
            details["Job Title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("location:"):
            details["Location"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("status:"):
            details["status"] = normalize_status(line.split(":",1)[1].strip())
    print(f"[DEBUG] Parsed classification details: {details}")
    return details

def normalize_email_date(email_date):
    if isinstance(email_date, int) and email_date > 1_000_000_000_000:
        try:
            return datetime.utcfromtimestamp(email_date / 1000).isoformat()
        except Exception as e:
            print(f"[WARN] Failed to convert email_date from ms: {e}")
    if isinstance(email_date, str):
        return email_date
    return datetime.utcnow().isoformat()

def save_results_to_bigquery(rows):
    dataset_ref = bigquery_client.dataset(BQ_DATASET_ID)
    table_ref   = dataset_ref.table(BQ_RAW_TABLE_ID)

    # 1) Ensure dataset exists
    try:
        bigquery_client.get_dataset(dataset_ref)
    except NotFound:
        print(f"[DEBUG] Dataset {BQ_DATASET_ID} not found, creating it…")
        ds = bigquery.Dataset(dataset_ref)
        ds.location = LOCATION
        bigquery_client.create_dataset(ds)
        print(f"[DEBUG] Created dataset {BQ_DATASET_ID} in {LOCATION}")

    # 2) Ensure table exists
    try:
        bigquery_client.get_table(table_ref)
    except NotFound:
        print(f"[DEBUG] Table {BQ_RAW_TABLE_ID} not found, creating it…")
        schema = [
            bigquery.SchemaField("user_id",           "STRING"),
            bigquery.SchemaField("email_id",          "STRING"),
            bigquery.SchemaField("company",           "STRING"),
            bigquery.SchemaField("job_title",         "STRING"),
            bigquery.SchemaField("location",          "STRING"),
            bigquery.SchemaField("status",            "STRING"),
            bigquery.SchemaField("inserted_at",       "TIMESTAMP"),
            bigquery.SchemaField("email_date",        "TIMESTAMP"),
            bigquery.SchemaField("raw_email_content", "STRING"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        bigquery_client.create_table(table)
        print(f"[DEBUG] Created table {BQ_DATASET_ID}.{BQ_RAW_TABLE_ID}")

    # 3) Insert
    print(f"[DEBUG] Inserting {len(rows)} rows into {BQ_DATASET_ID}.{BQ_RAW_TABLE_ID}")
    errors = bigquery_client.insert_rows_json(table_ref, rows)
    if errors:
        print("[ERROR] BigQuery insert errors:", errors)
    else:
        print(f"✅ Inserted {len(rows)} rows to BigQuery")

def save_results_to_firestore(data_dict, user_id, email_id):
    print(f"[DEBUG] Saving to Firestore for user {user_id}, email {email_id}")
    try:
        (firestore_client
            .collection('users')
            .document(user_id)
            .collection('job_applications')
            .document(email_id)
            .set(data_dict)
        )
        print(f"✅ Saved email {email_id} for user {user_id} to Firestore.")
    except Exception as e:
        print(f"[ERROR] Firestore save failed for email {email_id}, user {user_id}: {e}")

@app.route('/', methods=['POST'])
def index():
    print("[DEBUG] Received request")
    envelope = request.get_json(silent=True)
    if not envelope or 'message' not in envelope:
        print("[ERROR] Invalid Pub/Sub message.")
        return 'Invalid Pub/Sub message', 400

    message = envelope['message']
    if 'data' not in message:
        print("[ERROR] No data in Pub/Sub message.")
        return 'No data in message', 400

    try:
        pubsub_data   = base64.b64decode(message['data']).decode()
        print(f"[DEBUG] Decoded Pub/Sub data:\n{pubsub_data}")
        payload       = json.loads(pubsub_data)
        email_content = payload.get('email_content')
        user_id       = payload.get('user_id')
    except Exception as e:
        print(f"[ERROR] JSON decoding error: {e}")
        return 'Invalid JSON payload', 400

    if not email_content or not user_id:
        print("[ERROR] Missing email_content or user_id.")
        return 'Missing email_content or user_id', 400

    email_id = payload.get('email_id', f"local-{uuid.uuid4()}")
    print(f"[DEBUG] Processing email for user: {user_id}, email_id: {email_id}")

    classification = classify_email(email_content)
    if "not job application" in classification.lower():
        print(f"[DEBUG] Email {email_id} skipped (not job application).")
        return 'Email classified as not job application', 200

    details = parse_classification_details(classification)
    details.update({
        "email_id":   email_id,
        "user_id":    user_id,
        "inserted_at": datetime.utcnow().isoformat(),
        "email_date": normalize_email_date(payload.get("email_date")),
    })

    bq_row = {
        "user_id":           details["user_id"],
        "email_id":          details["email_id"],
        "company":           details["Company"],
        "job_title":         details["Job Title"],
        "location":          details["Location"],
        "status":            details["status"],
        "inserted_at":       details["inserted_at"],
        "email_date":        details["email_date"],
        "raw_email_content": email_content,
    }
    save_results_to_bigquery([bq_row])

    firestore_data = {
        "company":                details["Company"],
        "job_title":              details["Job Title"],
        "location":               details["Location"],
        "status":                 details["status"],
        "inserted_at":            details["inserted_at"],
        "email_date":             details["email_date"],
        "raw_email_content_snippet": email_content[:500],
    }
    save_results_to_firestore(firestore_data, user_id, email_id)

    batch_event = {
        "batch_id":  str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "email_id":  email_id
    }
    publisher.publish(
        topic_path,
        json.dumps(batch_event).encode(),
        content_type="batch-ready"
    )
    print(f"[DEBUG] Published batch-ready event for email_id={email_id}")

    return 'Email processed successfully', 200

if __name__ == '__main__':
    print("[DEBUG] Running Cloud Run service locally.")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
