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
- **Authentication**: Firebase Auth with Google OAuth
- **UI Library**: Material-UI (MUI) v7 with custom design system
- **Charts & Visualization**: Recharts for data analytics
- **State Management**: React Context + Hooks
- **Routing**: React Router v7
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

## 🎨 Frontend Features

### User Interface
- **Landing Page**: Modern hero section with feature showcase and call-to-action
- **Authentication**: Complete auth flow with Firebase integration
  - Login/Signup pages with Google and Apple OAuth
  - Email verification flow
  - Password reset functionality
- **Dashboard**: 
  - Interactive sidebar navigation
  - Summary cards for key metrics (applications, interviews, offers, rejections)
  - Job applications table with status badges
  - Real-time data visualization with bar and pie charts
  - Gmail integration button for email syncing
- **Settings**: User profile management and preferences
- **Legal Pages**: Terms of Service and Privacy Policy
- **Error Handling**: Professional 404 page
- **Missing**: Profile and Applications detail pages (awaiting UI/UX designs)

### Design System
- **Color Palette**: Warm orange theme (#FF7043 accent, #FFD7B5 sidebar)
- **Typography**: Modern, clean fonts with proper hierarchy
- **Components**: Material-UI v7 with custom styling
- **Responsive**: Mobile-first design approach
- **Charts**: Recharts integration for data visualization

## 📈 Monitoring & Analytics

- **Cloud Logging**: Service logs and error tracking
- **BigQuery**: Job application analytics
- **dbt**: Data transformations and modeling
- **Firebase Analytics**: User behavior tracking

## 🚀 Deployment Status

- ✅ **Frontend**: Complete React app with Firebase Auth and full UI suite
- ✅ **Backend API**: FastAPI services (needs REST API layer)
- ✅ **AI Processing**: Vertex AI email classification
- ✅ **Data Storage**: BigQuery + Firestore
- ✅ **GCP Deployment**: Cloud Run services
- ✅ **UI/UX**: Complete Material-UI interface with all pages
- 🔄 **API Integration**: REST endpoints needed for frontend
- 🔄 **Analytics**: dbt transformations (planned)

## 🎯 Next Steps

### Backend Development (Priority)
1. **REST API Layer**: Create FastAPI endpoints to bridge frontend with existing services
   - `GET /api/applications` - Fetch user job applications from Firestore
   - `GET /api/dashboard/stats` - Dashboard analytics from BigQuery
   - `POST /api/gmail/connect` - Gmail OAuth integration
   - `POST /api/sync/trigger` - Manual email sync
   
2. **Data Integration**: Connect existing Firestore data to frontend
   - User-specific job application queries
   - Real-time data subscriptions
   - BigQuery analytics aggregation

3. **Authentication**: Add Firebase token validation to backend services
   - Middleware for protected routes
   - User session management
   - Email verification checks

### Frontend Development (Enhancement)
1. **Real Data Integration**: Replace dummy data once backend APIs are ready
   - Connect dashboard to live Firestore data
   - Implement Gmail OAuth flow
   - Add real-time data updates

2. **Advanced Features**: Add enhanced functionality
   - Application status updates
   - File upload for resumes/cover letters
   - Advanced search and filtering
   - Export functionality

3. **Performance Optimization**: Improve user experience
   - Implement caching strategies
   - Add skeleton loading states
   - Optimize bundle size

### Infrastructure (Optional)
1. **CI/CD Pipeline**: Automated testing and deployment
2. **Monitoring**: Error tracking and performance monitoring
3. **Security**: Security audits and penetration testing

## 📝 License

This project is proprietary and confidential.
