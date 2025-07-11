# backend/config.py

PROJECT_ID = "onlyjobs-465420"
LOCATION = "us-central1" # Consistent region
PUB_SUB_NEW_EMAILS_TOPIC = "new-emails-topic" # Name of the Pub/Sub topic
BQ_DATASET_ID = "user_data" # Your BigQuery dataset name
BQ_RAW_TABLE_ID = "job_applications" # Your BigQuery table name
FIRESTORE_DATABASE_ID = "emails-firestore"
# Add any other global configurations here