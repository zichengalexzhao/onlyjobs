# OnlyJobs - AI-Powered Job Application Tracker

An intelligent job application tracking system that automatically syncs with Gmail, uses AI to classify and extract job application details, and provides real-time analytics through a modern web dashboard.

## 🚀 Features

- **🔐 Secure Authentication**: Firebase Auth with email verification
- **📧 Gmail Integration**: Automatic email fetching and processing
- **🤖 AI-Powered Classification**: Google Vertex AI (Gemini 2.5 Flash) for intelligent email analysis
- **📊 Real-time Analytics**: BigQuery for data warehousing and dbt transformations
- **⚡ Cloud-Native**: Fully deployed on Google Cloud Platform
- **🔄 Event-Driven Architecture**: Pub/Sub for scalable email processing
- **📱 Modern UI**: React with TypeScript and responsive design

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   GCP Services  │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (Cloud Run)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Pub/Sub       │    │   Vertex AI     │
│   (Auth/DB)     │    │   (Events)      │    │   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   process_emails│              │
         │              │   (Cloud Run)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firestore     │    │   BigQuery      │    │   Analytics     │
│   (Real-time)   │    │   (Warehouse)   │    │   (dbt)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
onlyjobs/
├── frontend/                    # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Route components
│   │   ├── contexts/          # React contexts (Auth)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API and external services
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Utility functions
│   └── package.json
├── backend/                    # Backend services and functions
│   ├── api/                   # FastAPI application
│   ├── services/
│   │   └── process_emails/    # AI email processing service
│   ├── functions/
│   │   └── gmail_fetch/       # Gmail integration functions
│   ├── config.py              # GCP configuration
│   └── tests/                 # Backend tests
├── backend_launch_and_tests/   # Deployment and testing notebooks
│   ├── deployments.ipynb      # GCP deployment orchestration
│   └── integration_tests.ipynb # End-to-end testing
└── docs/                      # Architecture and API documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Google Cloud Platform account
- Firebase project
- Gmail API access

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### GCP Deployment

1. **Set up GCP project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   gcloud config set run/region us-central1
   ```

2. **Deploy services**:
   ```bash
   # Run the deployment notebook
   jupyter notebook backend_launch_and_tests/deployments.ipynb
   ```

3. **Configure Pub/Sub triggers**:
   - Set up `new-emails-topic` in Google Cloud Console
   - Configure push subscription to `process-emails` service

## 🔧 Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Authentication**: Firebase Auth
- **UI Library**: Chakra UI (planned)
- **State Management**: React Context + Hooks
- **Build Tool**: Create React App

### Backend
- **API Framework**: FastAPI
- **Cloud Platform**: Google Cloud Run
- **AI/ML**: Google Vertex AI (Gemini 2.5 Flash)
- **Message Queue**: Google Cloud Pub/Sub
- **Data Warehouse**: Google BigQuery
- **Real-time DB**: Google Firestore
- **Containerization**: Docker

### Infrastructure
- **Deployment**: Google Cloud Build
- **Orchestration**: Jupyter Notebooks
- **Monitoring**: Google Cloud Logging
- **Testing**: Integration tests with Jupyter

## 🤖 AI Email Processing

The system uses Google Vertex AI with Gemini 2.5 Flash to:

1. **Classify emails** as job-related or not
2. **Extract structured data**:
   - Company name
   - Job title
   - Location
   - Application status (Applied, Interviewed, Declined, Offer)
3. **Store results** in both BigQuery (analytics) and Firestore (real-time)

### Processing Flow

```
Gmail Email → Pub/Sub → process_emails Service → Vertex AI → BigQuery + Firestore
```

## 📊 Data Architecture

- **BigQuery**: Raw job application data for analytics and dbt transformations
- **Firestore**: Real-time job application data for frontend dashboard
- **Firebase Auth**: User authentication and session management

## 🔒 Security

- **Authentication**: Firebase Auth with email verification
- **Authorization**: Protected routes and API endpoints
- **Data Encryption**: GCP-managed encryption at rest and in transit
- **IAM**: Least-privilege access for all services

## 🧪 Testing

- **Unit Tests**: Backend service tests
- **Integration Tests**: End-to-end testing via Jupyter notebooks
- **Manual Testing**: Cloud Logging monitoring and BigQuery verification

## 👥 Team

[Andrew Ting](https://github.com/AndrewTing89)

[Xianglong (Jason) Wang](https://github.com/XianglongWang)

[Zicheng (Alex) Zhao](https://github.com/zichengalexzhao)

## 🔄 Git Workflow

### Branching Strategy

1. **Main branch**: `main` (production-ready)
2. **Development branch**: `develop` (integration)
3. **Feature branches**: `feature/your-feature-name`

### Workflow

```bash
# Create development branch
git checkout -b develop
git push -u origin develop

# Create feature branch from develop
git checkout -b feature/your-feature
# ... work on feature ...
git push origin feature/your-feature

# Create PR to develop
# After review, merge to develop

# When ready for production
git checkout main
git merge develop
git push origin main
```

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`):
```
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_API_BASE_URL=http://localhost:8080
```

**Backend** (Cloud Run environment):
```
PROJECT_ID=onlyjobs-465420
LOCATION=us-central1
BQ_DATASET_ID=user_data
BQ_RAW_TABLE_ID=job_applications
FIRESTORE_DATABASE_ID=emails-firestore
```

## 📈 Monitoring & Analytics

- **Cloud Logging**: Service logs and error tracking
- **BigQuery**: Job application analytics
- **dbt**: Data transformations and modeling
- **Firebase Analytics**: User behavior tracking

## 🚀 Deployment Status

- ✅ **Frontend**: React app with Firebase Auth
- ✅ **Backend API**: FastAPI services
- ✅ **AI Processing**: Vertex AI email classification
- ✅ **Data Storage**: BigQuery + Firestore
- ✅ **GCP Deployment**: Cloud Run services
- 🔄 **UI/UX**: Placeholder pages (design in progress)
- 🔄 **Analytics**: dbt transformations (planned)

## 📝 License

This project is proprietary and confidential.
