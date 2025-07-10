# Authentication Infrastructure Documentation

## Overview

This document explains the authentication infrastructure for OnlyJobs. All auth logic is implemented and ready for UI components to be connected.

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
  
  // Methods
  signup,           // (email, password, displayName?) => Promise
  login,            // (email, password) => Promise
  logout,           // () => Promise
  loginWithGoogle,  // () => Promise
  resetPassword,    // (email) => Promise
  updateUserProfile,// (displayName) => Promise
  sendVerificationEmail, // () => Promise
  getIdToken,       // () => Promise<string>
} = useAuth();
```

## For Backend Developer

### Expected API Endpoints

Your API should handle these endpoints:

```typescript
// User Management
POST   /api/users              // Create user profile on signup
GET    /api/users/me           // Get current user profile
PUT    /api/users/me           // Update user profile

// Gmail Integration
GET    /api/gmail/auth-url     // Return Google OAuth URL
POST   /api/gmail/callback     // Handle OAuth callback
DELETE /api/gmail/disconnect   // Remove Gmail connection

// Sync Operations
POST   /api/sync/trigger       // Start email sync
GET    /api/sync/status        // Get sync status

// Job Applications (examples)
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

## Integration Checklist

### Frontend Team

* [ ]  Create login/signup UI components
* [ ]  Connect forms to auth methods
* [ ]  Add loading states during auth
* [ ]  Display error messages
* [ ]  Create email verification page
* [ ]  Build dashboard layout

### Backend Team

* [ ]  Implement all API endpoints
* [ ]  Set up Firebase Admin SDK
* [ ]  Configure CORS for frontend URL
* [ ]  Create BigQuery user tables
* [ ]  Implement Gmail OAuth flow
* [ ]  Add token verification middleware

## Questions?

* Frontend auth issues: Check AuthContext.tsx
* API integration: See services/api.service.ts
* Type definitions: Check types/ folder
