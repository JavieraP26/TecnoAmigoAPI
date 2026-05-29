import * as SecureStore from 'expo-secure-store';

const KEYS = {
  accessToken: 'access_token',
  refreshToken: 'refresh_token',
} as const;

export const storage = {
  async getAccessToken(): Promise<string | null> {
    return SecureStore.getItemAsync(KEYS.accessToken);
  },
  async setAccessToken(token: string): Promise<void> {
    await SecureStore.setItemAsync(KEYS.accessToken, token);
  },
  async getRefreshToken(): Promise<string | null> {
    return SecureStore.getItemAsync(KEYS.refreshToken);
  },
  async setRefreshToken(token: string): Promise<void> {
    await SecureStore.setItemAsync(KEYS.refreshToken, token);
  },
  async clearTokens(): Promise<void> {
    await SecureStore.deleteItemAsync(KEYS.accessToken);
    await SecureStore.deleteItemAsync(KEYS.refreshToken);
  },
};
