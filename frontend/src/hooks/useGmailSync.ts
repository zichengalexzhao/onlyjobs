// useGmailSync.ts
import { useState, useCallback } from 'react';
import { gmailService } from '../services/gmail.service';
import { useAuth } from '../contexts/AuthContext';

interface SyncState {
  isSyncing: boolean;
  lastSync: Date | null;
  error: string | null;
  progress: number;
}

export function useGmailSync() {
  const { currentUser } = useAuth();
  const [syncState, setSyncState] = useState<SyncState>({
    isSyncing: false,
    lastSync: null,
    error: null,
    progress: 0,
  });

  const startSync = useCallback(async () => {
    if (!currentUser) {
      setSyncState(prev => ({ ...prev, error: 'User not authenticated' }));
      return;
    }

    setSyncState({
      isSyncing: true,
      lastSync: null,
      error: null,
      progress: 0,
    });

    try {
      // Trigger sync
      const response = await gmailService.triggerSync();
      
      // Poll for status (you can implement WebSocket later)
      const pollStatus = setInterval(async () => {
        try {
          const status = await gmailService.getSyncStatus();
          
          if (!status.isRunning) {
            clearInterval(pollStatus);
            setSyncState({
              isSyncing: false,
              lastSync: new Date(),
              error: null,
              progress: 100,
            });
          } else {
            // Update progress (implement actual progress tracking)
            setSyncState(prev => ({
              ...prev,
              progress: Math.min(prev.progress + 10, 90),
            }));
          }
        } catch (error) {
          clearInterval(pollStatus);
          setSyncState(prev => ({
            ...prev,
            isSyncing: false,
            error: 'Failed to check sync status',
          }));
        }
      }, 2000);

      // Clear interval after max time
      setTimeout(() => clearInterval(pollStatus), 60000);
      
    } catch (error) {
      setSyncState({
        isSyncing: false,
        lastSync: null,
        error: error instanceof Error ? error.message : 'Sync failed',
        progress: 0,
      });
    }
  }, [currentUser]);

  const connectGmail = useCallback(async () => {
    try {
      const authUrl = await gmailService.getOAuthUrl();
      
      // Open OAuth popup
      const width = 500;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      
      const popup = window.open(
        authUrl,
        'gmail-oauth',
        `width=${width},height=${height},left=${left},top=${top}`
      );
      
      // Listen for OAuth callback
      window.addEventListener('message', async (event) => {
        if (event.origin !== window.location.origin) return;
        
        if (event.data.type === 'gmail-oauth-callback') {
          popup?.close();
          
          if (event.data.code) {
            await gmailService.handleOAuthCallback(event.data.code);
            // Start initial sync
            await startSync();
          }
        }
      });
      
    } catch (error) {
      console.error('Failed to connect Gmail:', error);
      throw error;
    }
  }, [startSync]);

  return {
    ...syncState,
    startSync,
    connectGmail,
  };
}