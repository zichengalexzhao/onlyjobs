#!/bin/bash

echo "🔧 OAuth Configuration Fix Script"
echo "=================================="

# Get current project
PROJECT_ID=$(gcloud config get-value project)
echo "Project: $PROJECT_ID"

# Get current user
USER_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo "Current user: $USER_EMAIL"

echo ""
echo "❌ The OAuth app is currently configured as 'Internal' but needs to be 'External'"
echo "❌ You need to manually configure the OAuth consent screen"
echo ""
echo "🔧 Required changes:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID"
echo "2. Click 'EDIT APP'"
echo "3. Change 'User Type' from 'Internal' to 'External'"
echo "4. In 'App Information':"
echo "   - App name: onlyjobs"
echo "   - User support email: $USER_EMAIL"
echo "   - Developer contact email: $USER_EMAIL"
echo "5. In 'Scopes', add these scopes:"
echo "   - ../auth/gmail.readonly"
echo "   - ../auth/gmail.labels"
echo "   - ../auth/userinfo.email"
echo "   - ../auth/userinfo.profile"
echo "   - openid"
echo "6. In 'Test users', add: $USER_EMAIL"
echo "7. Save and continue through all steps"
echo "8. DO NOT publish the app - keep it in 'Testing' mode"
echo ""
echo "🚀 After making these changes, test the OAuth flow at:"
echo "   http://localhost:3000/oauth-test"
echo ""
echo "💡 Alternative: If you want to avoid manual config, I can help set up"
echo "   the backend to work with a different approach."