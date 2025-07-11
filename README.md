# OnlyJobs - Job Application Tracker

An automated job application tracking system that syncs with Gmail and uses AI to organize your job search

## **🚀 Quick Start**

### **Prerequisites**

* Node.js 18+
* Python 3.9+
* GCP Account
* Firebase Project

### **Frontend Setup**

```bash
cd frontend npm install npm start
```

### **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## **📁 Project Structure**

* `/frontend` - React application with Firebase Auth
* `/backend` - FastAPI backend services
* `/docs` - Architecture and API documentation

## 👥 Team

[Andrew Ting](https://github.com/AndrewTing89)

[Xianglong (Jason) Wang](https://github.com/XianglongWang)

[Zicheng (Alex) Zhao](https://github.com/zichengalexzhao)

## **🔧 Tech Stack**

* **Frontend**: React, TypeScript, Firebase Auth, Chakra UI
* **Backend**: FastAPI, Google Cloud Run, BigQuery
* **AI**: OpenAI API for email classification
* **Analytics**: dbt for data transformations EOF

## **Commit everything**

```bash
git add .
git commit -m "Add comprehensive project structure and documentation"
git push origin main
```

## **🔄 Setting Up Git Workflow**

Create a simple branching strategy:

```bash
# Create development branch
git checkout -b develop
git push -u origin develop

# Create your feature branch
git checkout -b feature/firebase-auth
```

## **Git Workflow**

1. Main branch: `main` (production-ready)
2. Development branch: `develop` (integration)
3. Feature branches: `feature/your-feature-name`

### **How to work**

Always create feature branches from `develop`

Make pull requests to `develop` - Only merge `develop` to `main` when ready for production

## 🔧 Configuration Update (IMPORTANT)

As of [date], we've migrated to the official GCP/Firebase project. All team members need to:
1. Get the new Firebase configuration from the team lead
2. Update your `.env.local` file with the new values
3. Restart your development server

Never commit `.env.local` files!
