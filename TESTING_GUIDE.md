# Gmail OAuth Integration - Testing Guide

## Overview
This guide covers how to test the Gmail OAuth integration that connects the frontend React app with the backend Cloud Function for token management.

## Prerequisites

### Backend Setup (A's Tasks)
1. **Deploy the Cloud Function** using the deployment notebook
2. **Set environment variables**:
   - `GOOGLE_OAUTH_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET`: Your Google OAuth client secret
   - `GOOGLE_OAUTH_REDIRECT_URI`: Set to `http://localhost:3000` for local testing
   - `PROJECT_ID`: Your GCP project ID

3. **Update OAuth settings in Google Cloud Console**:
   - Go to APIs & Services → Credentials
   - Add `http://localhost:3000` to Authorized redirect URIs
   - Note the Cloud Function URL (e.g., `https://us-central1-onlyjobs-465420.cloudfunctions.net/manage-tokens`)

### Frontend Setup (Your Tasks)
1. **Set environment variable**:
   ```bash
   # In frontend/.env.local
   REACT_APP_MANAGE_TOKENS_URL=https://us-central1-onlyjobs-465420.cloudfunctions.net/manage-tokens
   ```

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

## Testing Steps

### 1. Local Development Testing

1. **Start the frontend**:
   ```bash
   cd frontend
   npm start
   ```

2. **Navigate to Settings page** or the test page:
   - Settings: `http://localhost:3000/settings`
   - Test page: `http://localhost:3000/gmail-test` (you'll need to add this route)

3. **Test the OAuth flow**:
   - Click "Connect Gmail Account"
   - Should open Google OAuth popup
   - Grant permissions
   - Popup closes, success message appears
   - Sync status component becomes available

### 2. End-to-End Testing

#### Test Cases:

**✅ OAuth Connection Flow**
- [ ] Click "Connect Gmail Account"
- [ ] Popup opens with Google OAuth screen
- [ ] User grants permissions
- [ ] Popup closes automatically
- [ ] Success message appears
- [ ] UI updates to show "Connected" state

**✅ Error Handling**
- [ ] Test popup blocked (disable popups in browser)
- [ ] Test user cancels OAuth (close popup manually)
- [ ] Test network errors (disable internet)
- [ ] Test invalid credentials

**✅ Sync Functionality**
- [ ] Click "Sync Now" button
- [ ] Loading state appears
- [ ] Progress indicator works
- [ ] Success message after completion

**✅ Disconnection**
- [ ] Click "Disconnect Gmail"
- [ ] Confirmation that disconnection worked
- [ ] UI updates to show "Not Connected" state

### 3. Debugging

#### Frontend Debugging:
```bash
# Check browser console for errors
# Check network tab for API calls
# Verify environment variables are loaded
```

#### Backend Debugging:
```bash
# Check Cloud Function logs
gcloud functions logs read manage-tokens --region us-central1

# Test endpoints directly
curl -X GET "https://us-central1-onlyjobs-465420.cloudfunctions.net/manage-tokens/api/gmail/auth-url"
```

#### Common Issues:
1. **"Failed to open OAuth popup"**: Check popup blocker
2. **"User not authenticated"**: Ensure Firebase auth is working
3. **"Failed to get OAuth URL"**: Check Cloud Function deployment
4. **CORS errors**: Verify Cloud Function CORS settings

### 4. Production Testing

1. **Deploy Cloud Function** with production OAuth settings
2. **Update redirect URI** to production domain
3. **Test with production build**:
   ```bash
   npm run build
   npm install -g serve
   serve -s build
   ```

## Component Documentation

### GmailConnection Component
- **Props**: `isConnected: boolean`, `onConnectionChange: (connected: boolean) => void`
- **Features**: OAuth flow, loading states, error handling
- **Location**: `src/components/GmailConnection.tsx`

### SyncStatus Component
- **Props**: `isConnected: boolean`, `compact?: boolean`
- **Features**: Sync progress, status indicators, manual sync
- **Location**: `src/components/SyncStatus.tsx`

### useGmailSync Hook
- **Returns**: `{ isConnecting, isSyncing, error, progress, connectGmail, disconnectGmail, startSync }`
- **Features**: OAuth management, sync state, error handling
- **Location**: `src/hooks/useGmailSync.ts`

## API Endpoints

### Cloud Function Endpoints:
- `GET /api/gmail/auth-url` - Get OAuth URL
- `POST /api/gmail/callback` - Handle OAuth callback
- `DELETE /api/gmail/disconnect` - Disconnect Gmail

### Expected Responses:
```json
// GET /api/gmail/auth-url
{
  "authUrl": "https://accounts.google.com/o/oauth2/v2/auth?..."
}

// POST /api/gmail/callback
// Status 200 with message

// DELETE /api/gmail/disconnect  
// Status 200 with message
```

## Next Steps

### For A (Backend):
1. **Implement missing endpoints**:
   - `POST /api/sync/trigger` - Trigger email sync
   - `GET /api/sync/status` - Get sync status
   - `GET /api/users/me` - Get user profile
   - `PUT /api/users/me` - Update user profile

2. **Complete email processing pipeline**:
   - Connect stored tokens to Gmail API
   - Implement email fetching logic
   - Set up BigQuery data storage

3. **Add authentication middleware** for protected endpoints

### For J (UI/UX):
1. **Design improvements**:
   - Add animations to sync progress
   - Improve error message styling
   - Add tooltips for better UX

2. **Dashboard integration**:
   - Show sync status in dashboard
   - Display processed emails
   - Add analytics views

### For You (Frontend):
1. **Add the test route** to your router
2. **Implement real-time sync updates** (WebSockets)
3. **Add data persistence** for connection state
4. **Improve error handling** with retry logic

## Security Considerations

1. **Never expose client secrets** in frontend code
2. **Use HTTPS** for all OAuth redirects
3. **Validate all user inputs** on backend
4. **Implement rate limiting** for API endpoints
5. **Log security events** for monitoring

## Performance Optimizations

1. **Lazy load components** for better initial load time
2. **Debounce sync requests** to prevent spam
3. **Cache OAuth tokens** securely
4. **Implement pagination** for large email lists
5. **Use React.memo** for component optimization

---

## Quick Start Commands

```bash
# Backend (A)
cd backend_launch_and_tests
jupyter notebook deployments.ipynb

# Frontend (You)
cd frontend
npm start
# Navigate to http://localhost:3000/settings

# Testing
# Click "Connect Gmail Account"
# Grant permissions in popup
# Test sync functionality
```

This integration provides a solid foundation for Gmail OAuth with proper error handling, beautiful UI components, and comprehensive testing capabilities.