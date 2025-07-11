# `process_emails` Cloud Run Service

This directory contains the code and configuration for the `process_emails` Cloud Run service, a core component of the Job Application Tracker application.

## 🚀 Purpose

The `process_emails` service is responsible for:
1.  Receiving raw email content via Google Cloud Pub/Sub messages.
2.  Classifying the email content to determine if it's a job application and extracting structured details (Company, Job Title, Location, Status) using Google Cloud Vertex AI (Gemini Flash model).
3.  Storing the classified, structured job application data into two destinations:
    * Google Cloud BigQuery (for analytical storage and dbt transformations).
    * Google Cloud Firestore (for real-time access by the frontend dashboard).

## 💡 How It Works (Data Flow)

This service acts as a **Pub/Sub Subscriber**.

1.  **Input:** It listens for incoming HTTP POST requests, which are sent by a Google Cloud Pub/Sub push subscription. These messages contain a base64-encoded JSON payload with `user_id`, `email_id`, `email_content`, and `email_date`.
2.  **Classification:** It decodes the message, extracts the `email_content`, and sends it to the Gemini Flash model deployed on Vertex AI for classification.
3.  **Data Storage:** Based on the classification result:
    * If classified as a job application, it parses the details and writes a record to both the configured BigQuery table and Firestore collection.
    * If classified as "Not Job Application", it logs the event and acknowledges the message without storing data.
4.  **Output:** Returns an HTTP 200 OK response to Pub/Sub, acknowledging successful message processing.

## 📦 Directory Contents

* `main.py`: The main entry point for the Cloud Run service. It sets up the Flask web server, handles Pub/Sub message ingestion, orchestrates the classification call, and manages saving data to BigQuery and Firestore.
* `classifier_logic.py`: Contains the core classification logic, including Vertex AI initialization, Gemini model loading, and the `is_job_application` and `classify_email` functions.
* `Dockerfile`: Defines how to build the Docker image for this service, including Python version, dependencies, and the Gunicorn server.
* `requirements.txt`: Lists all Python libraries required by `main.py` and `classifier_logic.py`.

## ⚙️ Configuration

This service relies on environment variables for configuration. These are passed during Cloud Run deployment (e.g., using `--set-env-vars`).

* `PROJECT_ID`: Your Google Cloud Project ID (e.g., `onlyjobs-465420`).
* `LOCATION`: The GCP region where services are deployed (e.g., `us-central1`).
* `BQ_DATASET_ID`: The ID of your BigQuery dataset (e.g., `user_data`).
* `BQ_RAW_TABLE_ID`: The ID of your BigQuery table for raw job applications (e.g., `job_applications`).
* `FIRESTORE_DATABASE_ID`: The ID of your named Firestore database (e.g., `emails-firestore`).

## 🚀 Deployment

This service is deployed as a Google Cloud Run service. The entire build and deployment process is orchestrated via the `deployment.ipynb` Jupyter Notebook located at the **project root**.

**Deployment Procedure (orchestrated by `deployment.ipynb`):**

1.  **Build Docker Image:** The `Dockerfile` in this directory is used by Google Cloud Build to create a Docker image, which is then pushed to Google Container Registry (GCR). This step is executed from `deployment.ipynb`.
    ```bash
    # Example command executed from deployment.ipynb (project root):
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/process-emails ./backend/services/process_emails
    ```
2.  **Deploy to Cloud Run:** The Docker image is deployed as a Cloud Run service. This command also sets the necessary environment variables for the service.
    ```bash
    # Example command executed from deployment.ipynb:
    gcloud run deploy process-emails --image gcr.io/YOUR_PROJECT_ID/process-emails --platform managed --region us-central1 --no-allow-unauthenticated --set-env-vars ...
    ```
3.  **Configure Pub/Sub Trigger (Manual Step):** After deployment, a Pub/Sub push subscription must be manually configured in the Google Cloud Console (Cloud Run service details -> Triggers tab), pointing to the `new-emails-topic`.

## 🔒 IAM Permissions

The **service account** associated with this Cloud Run service (e.g., `process-emails@YOUR_PROJECT_ID.iam.gserviceaccount.com` or the Compute Engine default service account) **must** have the following IAM roles on your Google Cloud Project:

* `Vertex AI User`
* `BigQuery Data Editor`
* `Datastore User` (for Firestore access)
* `Pub/Sub Subscriber`

## 🧪 Testing

Both local component testing and cloud integration testing are performed using Jupyter Notebooks.

* **Local Component Testing:**
    For development and debugging of the `main.py` and `classifier_logic.py` components in isolation, you can use a local test notebook (e.g., `test_process_emails_local.ipynb` if you created one in this directory).

* **Cloud Integration Testing (Phase 1 Validation):**
    After deploying the `process_emails` service to Cloud Run and configuring its IAM permissions and Pub/Sub trigger, its end-to-end functionality is validated using the `integration_tests.ipynb` Jupyter Notebook located at the **project root**.

    **Procedure within `integration_tests.ipynb`:**
    1.  The notebook **publishes a test message to the `new-emails-topic` Pub/Sub topic** using the `google-cloud-pubsub` client library. This action directly tests the Pub/Sub publishing functionality and its ability to trigger the Cloud Run service.
    2.  This Pub/Sub message then triggers the deployed `process-emails` Cloud Run service.

    **Verification Steps (Manual after publishing message):**
    1.  **Monitor Cloud Logging:** Go to the Google Cloud Console, navigate to Cloud Logging, and filter logs for your `process-emails` Cloud Run service. Look for success messages like "✅ Inserted ... to BigQuery" and "✅ Saved email ... to Firestore."
    2.  **Verify Data in BigQuery:** In the BigQuery Console, inspect the `user_data.job_applications` table. Run a `SELECT *` query or use the "Preview" tab to confirm the classified data for your `user_id` has been inserted.
    3.  **Verify Data in Firestore:** In the Firebase Console, navigate to "Firestore Database" -> "Data". Confirm that a `users` collection exists, containing a document for your `user_id`, and within that, a `job_applications` subcollection with your classified email data.

This comprehensive testing procedure confirms that Phase 1 is fully functional in the cloud environment.