import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  signInWithPopup,
  sendPasswordResetEmail,
  updateProfile,
  sendEmailVerification,
  GoogleAuthProvider,
  AuthError
} from 'firebase/auth';
import { auth, googleProvider, appleProvider, gmailProvider } from '../config/firebase';

// Types
interface AuthContextType {
  // Current user
  currentUser: User | null;
  loading: boolean;
  
  // Auth methods
  signup: (email: string, password: string, displayName?: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithApple: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updateUserProfile: (displayName: string) => Promise<void>;
  sendVerificationEmail: () => Promise<void>;
  
  // Token management
  getIdToken: () => Promise<string | null>;
  getIdTokenResult: () => Promise<any | null>;
  
  // Gmail integration
  connectGmail: () => Promise<void>;
  disconnectGmail: () => Promise<void>;
  isGmailConnected: boolean;
  getGmailToken: () => string | null;
  
  // User state
  isEmailVerified: boolean;
  isNewUser: boolean;
}

// Create context
const AuthContext = createContext<AuthContextType>({} as AuthContextType);

// Custom hook to use auth
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);
  const [isGmailConnected, setIsGmailConnected] = useState(false);

  // Listen for auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      setLoading(false);
      // Check if Gmail is connected when user changes
      if (user) {
        const gmailToken = localStorage.getItem('gmail_access_token');
        setIsGmailConnected(!!gmailToken);
      } else {
        setIsGmailConnected(false);
      }
    });

    return unsubscribe;
  }, []);

  // Signup function
  const signup = async (email: string, password: string, displayName?: string) => {
    try {
      // Create user
      const result = await createUserWithEmailAndPassword(auth, email, password);
      setIsNewUser(true);
      
      // Update display name if provided
      if (displayName && result.user) {
        await updateProfile(result.user, { displayName });
      }
      
      // Send verification email
      if (result.user) {
        await sendEmailVerification(result.user);
      }
      
      // Log signup event (for analytics)
      console.log('New user signed up:', result.user.uid);
      
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      setIsNewUser(false);
      
      // Log login event
      console.log('User logged in:', result.user.uid);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Google login
  const loginWithGoogle = async () => {
    try {
      // Add custom parameters for Google OAuth
      googleProvider.setCustomParameters({
        prompt: 'select_account'
      });
      
      const result = await signInWithPopup(auth, googleProvider);
      
      // Check if it's a new user
      const isNew = result.user.metadata.creationTime === result.user.metadata.lastSignInTime;
      setIsNewUser(isNew);
      
      // Get Google access token (might need for Gmail API later)
      const credential = GoogleAuthProvider.credentialFromResult(result);
      const token = credential?.accessToken;
      
      // Store Google token if needed for Gmail integration
      if (token) {
        sessionStorage.setItem('google_access_token', token);
      }
      
      console.log('Google login successful:', result.user.uid);
      
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  };

  // Apple login
  const loginWithApple = async () => {
    try {
      // Configure Apple OAuth
      appleProvider.addScope('email');
      appleProvider.addScope('name');
      
      const result = await signInWithPopup(auth, appleProvider);
      
      // Check if it's a new user
      const isNew = result.user.metadata.creationTime === result.user.metadata.lastSignInTime;
      setIsNewUser(isNew);
      
      console.log('Apple login successful:', result.user.uid);
      
    } catch (error) {
      console.error('Apple login error:', error);
      throw error;
    }
  };

  // Logout
  const logout = async () => {
    try {
      await signOut(auth);
      // Clear any stored tokens
      sessionStorage.removeItem('google_access_token');
      localStorage.removeItem('gmail_access_token');
      setIsGmailConnected(false);
      console.log('User logged out');
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  // Reset password
  const resetPassword = async (email: string) => {
    try {
      await sendPasswordResetEmail(auth, email);
      console.log('Password reset email sent to:', email);
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  };

  // Update user profile
  const updateUserProfile = async (displayName: string) => {
    if (!currentUser) throw new Error('No user logged in');
    
    try {
      await updateProfile(currentUser, { displayName });
      console.log('Profile updated');
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  };

  // Send verification email
  const sendVerificationEmail = async () => {
    if (!currentUser) throw new Error('No user logged in');
    
    try {
      await sendEmailVerification(currentUser);
      console.log('Verification email sent');
    } catch (error) {
      console.error('Verification email error:', error);
      throw error;
    }
  };

  // Get ID token for API calls
  const getIdToken = async (): Promise<string | null> => {
    if (!currentUser) return null;
    
    try {
      const token = await currentUser.getIdToken();
      return token;
    } catch (error) {
      console.error('Get ID token error:', error);
      return null;
    }
  };

  // Get ID token result (includes claims)
  const getIdTokenResult = async () => {
    if (!currentUser) return null;
    
    try {
      const tokenResult = await currentUser.getIdTokenResult();
      return tokenResult;
    } catch (error) {
      console.error('Get ID token result error:', error);
      return null;
    }
  };

  // Gmail integration functions
  const connectGmail = async () => {
    if (!currentUser) throw new Error('No user logged in');
    
    try {
      // Configure Gmail provider with custom parameters
      gmailProvider.setCustomParameters({
        prompt: 'consent',
        access_type: 'offline'
      });
      
      const result = await signInWithPopup(auth, gmailProvider);
      
      // Get Gmail access token
      const credential = GoogleAuthProvider.credentialFromResult(result);
      const token = credential?.accessToken;
      
      if (token) {
        // Store Gmail token separately for API calls
        localStorage.setItem('gmail_access_token', token);
        setIsGmailConnected(true);
        console.log('Gmail connected successfully');
      } else {
        throw new Error('Failed to get Gmail access token');
      }
      
    } catch (error) {
      console.error('Gmail connection error:', error);
      throw error;
    }
  };

  const disconnectGmail = async () => {
    try {
      // Remove stored Gmail token
      localStorage.removeItem('gmail_access_token');
      setIsGmailConnected(false);
      console.log('Gmail disconnected');
    } catch (error) {
      console.error('Gmail disconnection error:', error);
      throw error;
    }
  };

  const getGmailToken = (): string | null => {
    return localStorage.getItem('gmail_access_token');
  };

  // Context value
  const value: AuthContextType = {
    currentUser,
    loading,
    signup,
    login,
    logout,
    loginWithGoogle,
    loginWithApple,
    resetPassword,
    updateUserProfile,
    sendVerificationEmail,
    getIdToken,
    getIdTokenResult,
    connectGmail,
    disconnectGmail,
    isGmailConnected,
    getGmailToken,
    isEmailVerified: currentUser?.emailVerified || false,
    isNewUser
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Error handler helper
export const getAuthErrorMessage = (error: AuthError): string => {
  switch (error.code) {
    case 'auth/email-already-in-use':
      return 'This email is already registered.';
    case 'auth/invalid-email':
      return 'Invalid email address.';
    case 'auth/operation-not-allowed':
      return 'Operation not allowed.';
    case 'auth/weak-password':
      return 'Password is too weak. Please use at least 6 characters.';
    case 'auth/user-disabled':
      return 'This account has been disabled.';
    case 'auth/user-not-found':
      return 'No account found with this email.';
    case 'auth/wrong-password':
      return 'Incorrect password.';
    case 'auth/popup-closed-by-user':
      return 'Login popup was closed.';
    case 'auth/cancelled-popup-request':
      return 'Login popup was cancelled.';
    case 'auth/account-exists-with-different-credential':
      return 'An account already exists with the same email but different sign-in credentials.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
};