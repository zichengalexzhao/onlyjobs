# Authentication Infrastructure Documentation

## Overview

This document explains the complete authentication infrastructure for OnlyJobs. The system includes Firebase Auth, Gmail OAuth integration, and a Firebase ID token debug tool for backend testing.

## For Frontend Developers (UI/UX Implementation)

### Using Authentication in Components

#### 1. Check if User is Logged In

```typescript
import { useAuth } from '../contexts/AuthContext';

function YourComponent() {
  const { currentUser, loading } = useAuth();
  
  if (loading) return <LoadingSpinner />;
  
  if (currentUser) {
    // User is logged in
    return <div>Welcome {currentUser.email}</div>;
  }
  
  // User is not logged in
  return <div>Please log in</div>;
}
```

#### 2. Login Form Implementation

```typescript
import { useAuth } from '../contexts/AuthContext';
import { getAuthErrorMessage } from '../contexts/AuthContext';

function LoginForm() {
  const { login, loginWithGoogle } = useAuth();
  const [error, setError] = useState('');
  
  const handleEmailLogin = async (email: string, password: string) => {
    try {
      await login(email, password);
      // Redirect handled by router
    } catch (err) {
      setError(getAuthErrorMessage(err));
    }
  };
  
  const handleGoogleLogin = async () => {
    try {
      await loginWithGoogle();
    } catch (err) {
      setError(getAuthErrorMessage(err));
    }
  };
  
  // Your UI here
}
```

#### 3. Protected Pages

Pages are already protected! Just create the UI:

* `/dashboard` - Requires login + verified email
* `/settings` - Requires login + verified email
* `/verify-email` - Requires login only

### Available Auth Methods

```typescript
const {
  // State
  currentUser,      // Firebase User object or null
  loading,          // Boolean - auth state loading
  isEmailVerified,  // Boolean - email verified status
  isNewUser,        // Boolean - if just signed up
  isGmailConnected, // Boolean - Gmail OAuth status
  
  // Methods
  signup,           // (email, password, displayName?) => Promise
  login,            // (email, password) => Promise
  logout,           // () => Promise
  loginWithGoogle,  // () => Promise
  loginWithApple,   // () => Promise
  resetPassword,    // (email) => Promise
  updateUserProfile,// (displayName) => Promise
  sendVerificationEmail, // () => Promise
  getIdToken,       // () => Promise<string>
  getIdTokenResult, // () => Promise<any>
  
  // Gmail Integration
  connectGmail,     // () => Promise<void>
  disconnectGmail,  // () => Promise<void>
  getGmailToken,    // () => string | null
} = useAuth();
```

## For Backend Developer

### Current API Endpoints

✅ **Implemented Backend Endpoints** (Andrew):

```typescript
// Gmail Integration (Cloud Run: https://manage-tokens-12002195951.us-central1.run.app)
POST   /api/gmail/auth-url     // Return Google OAuth URL
POST   /api/gmail/callback     // Handle OAuth callback
POST   /api/gmail/disconnect   // Remove Gmail connection

// 🔄 Still Needed:
// User Management
POST   /api/users              // Create user profile on signup
GET    /api/users/me           // Get current user profile
PUT    /api/users/me           // Update user profile

// Sync Operations
POST   /api/sync/trigger       // Start email sync
GET    /api/sync/status        // Get sync status

// Job Applications
GET    /api/applications       // Get user's applications
GET    /api/applications/stats // Get dashboard statistics
```

### Authentication Format

All API requests include Firebase ID token:

```
Authorization: Bearer <firebase-id-token>
```

### Verifying Tokens (Python Example)

```python
from firebase_admin import auth

async def verify_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        return user_id
    except:
        raise HTTPException(401, "Invalid token")
```

### User ID

Always use Firebase UID as the primary user identifier:

```typescript
const userId = currentUser.uid;  // e.g., "aBcD1234..."
```

## Environment Setup

### Required Environment Variables

Copy `.env.example` to `.env.local` and fill in:

```
REACT_APP_API_BASE_URL=http://localhost:8080
REACT_APP_FIREBASE_API_KEY=your-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-domain
REACT_APP_FIREBASE_PROJECT_ID=your-project
REACT_APP_FIREBASE_STORAGE_BUCKET=your-bucket
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender
REACT_APP_FIREBASE_APP_ID=your-app
```

### Firebase Console Setup

1. Enable Authentication providers:
   * Email/Password
   * Google
2. Add authorized domains:
   * localhost
   * Your production domain

## Testing Authentication

### Manual Testing

1. Sign up with email/password
2. Check email verification flow
3. Test Google login
4. Test password reset
5. Verify protected routes work

### Common Issues

* **"Firebase not initialized"**: Check .env.local file
* **Google login popup blocked**: Allow popups for localhost
* **API calls failing**: Check CORS settings on backend

## File Structure

```
src/
├── contexts/
│   └── AuthContext.tsx       # Main auth logic
├── services/
│   ├── api.service.ts        # API communication
│   ├── auth.service.ts       # Auth-specific API calls
│   └── gmail.service.ts      # Gmail integration
├── hooks/
│   ├── useLocalStorage.ts    # Persistent storage
│   ├── useApi.ts            # API call wrapper
│   └── useGmailSync.ts      # Gmail sync logic
├── components/
│   ├── ProtectedRoute.tsx   # Route protection
│   └── LoadingSpinner.tsx   # Loading states
└── utils/
    ├── auth.utils.ts        # Auth helpers
    ├── date.utils.ts        # Date formatting
    └── validation.utils.ts  # Form validation
```

## 🔧 Firebase ID Token Debug Tool

### For Backend Testing

A debug tool has been added to the Settings page to help with backend development and testing:

**Location**: Settings Page → Developer Tools section

**Functionality**:
- Click "Get Token" button to retrieve current user's Firebase ID token
- Token is logged to browser console with clear formatting
- Easy copy-paste for manual backend testing

**Usage**:
```bash
# Example backend testing with retrieved token
curl -X POST https://manage-tokens-12002195951.us-central1.run.app/api/gmail/auth-url \
  -H "Authorization: Bearer <COPIED_TOKEN>" \
  -H "Content-Type: application/json"
```

**Implementation**: `src/pages/Settings.tsx:102-127`

## Integration Checklist

### Frontend Team ✅ COMPLETE

* [x]  Create login/signup UI components
* [x]  Connect forms to auth methods  
* [x]  Add loading states during auth
* [x]  Display error messages
* [x]  Create email verification page
* [x]  Build dashboard layout
* [x]  Implement Gmail OAuth integration UI
* [x]  Add Firebase token debug tool
* [x]  Create navigation paths to settings

### Backend Team

* [x]  Set up Firebase Admin SDK ✅
* [x]  Configure CORS for frontend URL ✅
* [x]  Implement Gmail OAuth flow ✅
* [x]  Add token verification middleware ✅
* [ ]  Create BigQuery user tables 🔄
* [ ]  Implement remaining API endpoints 🔄
* [ ]  Connect OAuth tokens to email processing 🔄

## Questions?

* Frontend auth issues: Check AuthContext.tsx
* API integration: See services/api.service.ts
* Type definitions: Check types/ folder
