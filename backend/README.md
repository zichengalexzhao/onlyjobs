# Backend - AI-Powered Email Processing Services

This directory contains the backend services for the OnlyJobs application, featuring AI-powered email classification and processing using Google Cloud Platform services.

## 🏗️ Architecture Overview

The backend consists of multiple microservices deployed on Google Cloud Platform:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gmail API     │    │   Pub/Sub       │    │   process_emails│
│   Integration   │───►│   new-emails-   │───►│   (Cloud Run)   │
│   (Functions)   │    │   topic         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Vertex AI     │
                                              │   (Gemini 2.5   │
                                              │   Flash)        │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   Data Storage  │
                                              │   BigQuery +    │
                                              │   Firestore     │
                                              └─────────────────┘
```

## 📁 Directory Structure

```
backend/
├── api/                          # FastAPI application
├── services/
│   └── process_emails/           # AI email processing service
│       ├── main.py              # Flask app for Cloud Run
│       ├── classifier_logic.py  # Vertex AI integration
│       ├── Dockerfile           # Container configuration
│       ├── requirements.txt     # Python dependencies
│       └── README_process_emails.md
├── functions/
│   └── gmail_fetch/             # Gmail API integration
│       └── gmail_fetch_gcp.py   # Email fetching logic
├── config.py                    # GCP configuration
├── tests/                       # Backend tests
└── backup/                      # Backup configurations
```

## 🤖 Core Services

### 1. process_emails Service

**Purpose**: AI-powered email classification and data extraction

**Key Features**:
- Receives emails via Google Cloud Pub/Sub
- Uses Vertex AI (Gemini 2.5 Flash) for intelligent classification
- Extracts structured job application data
- Stores results in BigQuery and Firestore

**Deployment**: Google Cloud Run service

**Configuration**:
```python
PROJECT_ID = "onlyjobs-465420"
LOCATION = "us-central1"
BQ_DATASET_ID = "user_data"
BQ_RAW_TABLE_ID = "job_applications"
FIRESTORE_DATABASE_ID = "emails-firestore"
```

### 2. Gmail Integration Functions

**Purpose**: Fetch and process emails from Gmail

**Key Features**:
- Gmail API integration with OAuth2
- Email content extraction and parsing
- Pub/Sub message publishing for processing

**Location**: `functions/gmail_fetch/gmail_fetch_gcp.py`

## 🔧 Configuration

### Environment Variables

The backend services use the following environment variables:

```bash
# GCP Project Configuration
PROJECT_ID=onlyjobs-465420
LOCATION=us-central1

# Pub/Sub Configuration
PUB_SUB_NEW_EMAILS_TOPIC=new-emails-topic

# BigQuery Configuration
BQ_DATASET_ID=user_data
BQ_RAW_TABLE_ID=job_applications

# Firestore Configuration
FIRESTORE_DATABASE_ID=emails-firestore
```

### Configuration File

`config.py` contains the centralized configuration:

```python
PROJECT_ID = "onlyjobs-465420"
LOCATION = "us-central1"
PUB_SUB_NEW_EMAILS_TOPIC = "new-emails-topic"
BQ_DATASET_ID = "user_data"
BQ_RAW_TABLE_ID = "job_applications"
FIRESTORE_DATABASE_ID = "emails-firestore"
```

## 🚀 Deployment

### Prerequisites

1. **Google Cloud Platform Account**
2. **GCP Project Setup**:
   ```bash
   gcloud config set project onlyjobs-465420
   gcloud config set run/region us-central1
   ```

3. **Required APIs Enabled**:
   - Cloud Run API
   - Cloud Build API
   - Pub/Sub API
   - BigQuery API
   - Firestore API
   - Vertex AI API

### Deployment Process

1. **Build and Deploy Services**:
   ```bash
   # Run the deployment notebook
   jupyter notebook ../backend_launch_and_tests/deployments.ipynb
   ```

2. **Manual Configuration**:
   - Set up Pub/Sub topic: `new-emails-topic`
   - Configure push subscription to `process-emails` service
   - Set up IAM permissions for service accounts

### Service Accounts and IAM

The `process-emails` service requires the following IAM roles:

- `Vertex AI User` - For AI model access
- `BigQuery Data Editor` - For data insertion
- `Datastore User` - For Firestore access
- `Pub/Sub Subscriber` - For message consumption

## 🧪 Testing

### Local Testing

```bash
# Test process_emails service locally
cd services/process_emails
python main.py
```

### Integration Testing

Use the integration testing notebook:

```bash
jupyter notebook ../backend_launch_and_tests/integration_tests.ipynb
```

### Testing Workflow

1. **Publish test message** to Pub/Sub topic
2. **Monitor Cloud Logging** for service execution
3. **Verify data insertion** in BigQuery
4. **Check Firestore** for real-time data

## 📊 Data Flow

### Email Processing Pipeline

1. **Email Reception**: Gmail API fetches new emails
2. **Message Publishing**: Email content published to Pub/Sub
3. **AI Classification**: Vertex AI analyzes email content
4. **Data Extraction**: Structured data extracted (Company, Job Title, Location, Status)
5. **Data Storage**: Results saved to BigQuery and Firestore

### Data Schema

**BigQuery Table** (`user_data.job_applications`):
```sql
CREATE TABLE job_applications (
    user_id STRING,
    email_id STRING,
    company STRING,
    job_title STRING,
    location STRING,
    status STRING,
    inserted_at TIMESTAMP,
    email_date DATE,
    raw_email_content STRING
);
```

**Firestore Collection** (`users/{user_id}/job_applications/{email_id}`):
```json
{
    "company": "string",
    "job_title": "string",
    "location": "string",
    "status": "string",
    "inserted_at": "timestamp",
    "email_date": "date",
    "raw_email_content_snippet": "string"
}
```

## 🔒 Security

### Authentication & Authorization

- **Service-to-Service**: GCP IAM and service accounts
- **API Access**: Firebase Auth tokens
- **Data Encryption**: GCP-managed encryption at rest and in transit

### Best Practices

- Least-privilege IAM roles
- Environment variable configuration
- Secure credential management
- Input validation and sanitization

## 📈 Monitoring

### Cloud Logging

Monitor service execution through Google Cloud Logging:

```bash
# View process_emails service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=process-emails"
```

### Key Metrics

- Email processing success rate
- AI classification accuracy
- Data insertion performance
- Service response times

## 🛠️ Development

### Local Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r services/process_emails/requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export PROJECT_ID="onlyjobs-465420"
   export LOCATION="us-central1"
   # ... other variables
   ```

3. **Run Services Locally**:
   ```bash
   # Run process_emails service
   cd services/process_emails
   python main.py
   ```

### Code Structure

- **main.py**: Flask application entry point
- **classifier_logic.py**: AI classification logic
- **gmail_fetch_gcp.py**: Gmail API integration
- **config.py**: Centralized configuration

## 🔄 CI/CD

### Deployment Pipeline

1. **Code Changes**: Push to feature branch
2. **Testing**: Run integration tests
3. **Build**: Cloud Build creates Docker images
4. **Deploy**: Cloud Run deployment
5. **Verification**: Integration test validation

### Deployment Commands

```bash
# Build Docker image
gcloud builds submit --tag gcr.io/onlyjobs-465420/process-emails ./services/process_emails

# Deploy to Cloud Run
gcloud run deploy process-emails \
  --image gcr.io/onlyjobs-465420/process-emails \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars PROJECT_ID=onlyjobs-465420,LOCATION=us-central1
```

## 📝 API Documentation

### process_emails Service Endpoints

**POST /** - Process email via Pub/Sub
- **Input**: Pub/Sub message with base64-encoded JSON
- **Output**: HTTP 200 OK on success
- **Authentication**: Pub/Sub push subscription

### Message Format

```json
{
  "user_id": "string",
  "email_id": "string", 
  "email_content": "string",
  "email_date": "YYYY-MM-DD"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **IAM Permission Errors**: Check service account roles
2. **Pub/Sub Connection**: Verify topic and subscription configuration
3. **Vertex AI Access**: Ensure API is enabled and credentials are set
4. **BigQuery Errors**: Check dataset and table permissions

### Debug Commands

```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision"

# Verify IAM permissions
gcloud projects get-iam-policy onlyjobs-465420

# Test Pub/Sub connectivity
gcloud pubsub topics publish new-emails-topic --message="test"
```

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
