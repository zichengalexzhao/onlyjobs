# backend/functions/dbt_trigger/main.py

import os
from googleapiclient.discovery import build

PROJECT_ID = os.environ["PROJECT_ID"]
DBT_DIR    = os.environ.get("DBT_DIR", "backend/dbt")
DBT_TARGET = os.environ.get("DBT_TARGET", "dev")

def run_dbt(event, context):
    """Background Cloud Function triggered by Pub/Sub."""
    # event['data'] is base64-encoded message; you can decode if needed.
    cb = build("cloudbuild", "v1", cache_discovery=False)
    build_body = {
        "steps": [
          {
            "name": "python:3.9-slim",
            "entrypoint": "bash",
            "args": [
              "-c",
              f"pip install dbt-bigquery && "
              f"cd {DBT_DIR} && "
              f"dbt run --profiles-dir . --target {DBT_TARGET} --select app_dashboard_metrics"
            ]
          }
        ],
        "timeout": "600s"
    }
    resp = cb.projects().builds().create(
        projectId=PROJECT_ID,
        body=build_body
    ).execute()
    print(f"🔔 Triggered Cloud Build: {resp['metadata']['build']['id']}")
