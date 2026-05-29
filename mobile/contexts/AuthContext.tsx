import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { router } from 'expo-router';
import api from '@/lib/api';
import { storage } from '@/lib/storage';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<(AuthState & AuthActions) | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
  });

  // Al arrancar, comprueba si hay token guardado
  useEffect(() => {
    (async () => {
      const token = await storage.getAccessToken();
      setState({ isAuthenticated: !!token, isLoading: false });
    })();
  }, []);

  const login = useCallback(async (accessToken: string, refreshToken: string) => {
    await storage.setAccessToken(accessToken);
    await storage.setRefreshToken(refreshToken);
    setState({ isAuthenticated: true, isLoading: false });
    router.replace('/(app)');
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = await storage.getRefreshToken();
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch {
        // Si falla el logout remoto, igual limpiamos localmente
      }
    }
    await storage.clearTokens();
    setState({ isAuthenticated: false, isLoading: false });
    router.replace('/auth');
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider');
  return ctx;
}
