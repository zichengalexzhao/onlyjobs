// useGmailSync.ts
import { useState, useCallback } from 'react';
import { gmailService } from '../services/gmail.service';
import { useAuth } from '../contexts/AuthContext';

interface SyncState {
  isSyncing: boolean;
  lastSync: Date | null;
  error: string | null;
  progress: number;
  isConnecting: boolean;
}

export function useGmailSync() {
  const { currentUser } = useAuth();
  const [syncState, setSyncState] = useState<SyncState>({
    isSyncing: false,
    lastSync: null,
    error: null,
    progress: 0,
    isConnecting: false,
  });

  const startSync = useCallback(async () => {
    if (!currentUser) {
      setSyncState(prev => ({ ...prev, error: 'User not authenticated' }));
      return;
    }

    setSyncState(prev => ({
      ...prev,
      isSyncing: true,
      error: null,
      progress: 0,
    }));

    try {
      // For now, simulate sync since the sync endpoint isn't implemented yet
      // TODO: Replace with actual sync API call when available
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSyncState(prev => ({
        ...prev,
        isSyncing: false,
        lastSync: new Date(),
        progress: 100,
      }));
      
    } catch (error) {
      setSyncState(prev => ({
        ...prev,
        isSyncing: false,
        error: error instanceof Error ? error.message : 'Sync failed',
        progress: 0,
      }));
    }
  }, [currentUser]);

  const connectGmail = useCallback(async () => {
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    setSyncState(prev => ({
      ...prev,
      isConnecting: true,
      error: null,
    }));

    try {
      console.log('🔄 Starting OAuth flow...');
      console.log('Current user:', currentUser.email);
      
      const authUrl = await gmailService.getOAuthUrl();
      console.log('✅ OAuth URL retrieved:', authUrl);
      
      // Create a promise that resolves when OAuth is complete
      const oauthPromise = new Promise<string>((resolve, reject) => {
        // Open OAuth popup
        const width = 500;
        const height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        
        console.log('🔄 Opening OAuth popup...');
        console.log('Popup URL:', authUrl);
        
        const popup = window.open(
          authUrl,
          'gmail-oauth',
          `width=${width},height=${height},left=${left},top=${top}`
        );

        if (!popup) {
          console.error('❌ Failed to open OAuth popup');
          reject(new Error('Failed to open OAuth popup. Please allow popups for this site.'));
          return;
        }

        console.log('✅ OAuth popup opened successfully');

        // Check if popup was closed manually
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            console.log('❌ OAuth popup closed by user');
            clearInterval(checkClosed);
            reject(new Error('OAuth cancelled by user'));
          }
        }, 1000);

        // Listen for OAuth callback
        const messageHandler = (event: MessageEvent) => {
          console.log('📨 Received message:', event.data);
          if (event.origin !== window.location.origin) return;
          
          if (event.data.type === 'gmail-oauth-callback') {
            console.log('✅ OAuth callback received');
            clearInterval(checkClosed);
            window.removeEventListener('message', messageHandler);
            popup.close();
            
            if (event.data.code) {
              console.log('✅ Authorization code received:', event.data.code.substring(0, 20) + '...');
              resolve(event.data.code);
            } else {
              console.error('❌ No authorization code in callback');
              reject(new Error('OAuth failed: No authorization code received'));
            }
          }
        };

        window.addEventListener('message', messageHandler);

        // Handle manual URL check for redirect (fallback)
        const checkUrl = setInterval(() => {
          try {
            const url = popup.location.href;
            console.log('🔄 Checking popup URL:', url);
            if (url.includes('code=')) {
              console.log('✅ Authorization code found in URL');
              clearInterval(checkUrl);
              clearInterval(checkClosed);
              window.removeEventListener('message', messageHandler);
              
              const urlParams = new URLSearchParams(new URL(url).search);
              const code = urlParams.get('code');
              
              if (code) {
                console.log('✅ Authorization code extracted:', code.substring(0, 20) + '...');
                popup.close();
                resolve(code);
              } else {
                console.error('❌ No authorization code found in URL');
                reject(new Error('No authorization code found in URL'));
              }
            }
          } catch (e) {
            // Cross-origin error - this is expected
            const errorMessage = e instanceof Error ? e.message : 'Unknown error';
            console.log('🔄 Cross-origin error (expected):', errorMessage);
          }
        }, 1000);

        // Timeout after 5 minutes
        setTimeout(() => {
          console.log('⏰ OAuth timeout');
          clearInterval(checkUrl);
          clearInterval(checkClosed);
          window.removeEventListener('message', messageHandler);
          if (!popup.closed) {
            popup.close();
          }
          reject(new Error('OAuth timeout'));
        }, 5 * 60 * 1000);
      });

      // Wait for OAuth to complete
      console.log('🔄 Waiting for OAuth to complete...');
      const code = await oauthPromise;
      
      // Handle the OAuth callback
      console.log('🔄 Processing OAuth callback...');
      await gmailService.handleOAuthCallback(code);
      console.log('✅ OAuth callback processed successfully');
      
      setSyncState(prev => ({
        ...prev,
        isConnecting: false,
        error: null,
      }));

      // Start initial sync after successful connection
      await startSync();
      
    } catch (error) {
      setSyncState(prev => ({
        ...prev,
        isConnecting: false,
        error: error instanceof Error ? error.message : 'Failed to connect Gmail',
      }));
      throw error;
    }
  }, [currentUser, startSync]);

  const disconnectGmail = useCallback(async () => {
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    try {
      await gmailService.disconnect();
      setSyncState(prev => ({
        ...prev,
        lastSync: null,
        error: null,
      }));
    } catch (error) {
      setSyncState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to disconnect Gmail',
      }));
      throw error;
    }
  }, [currentUser]);

  return {
    ...syncState,
    startSync,
    connectGmail,
    disconnectGmail,
  };
}