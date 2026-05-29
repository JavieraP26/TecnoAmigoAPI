export const colors = {
  // Primario — verde TecnoAmigo
  primary: '#00a800',
  primaryLight: '#e6f4e6',
  primaryMid: '#dae7da',

  // Fondos
  background: '#f5f8f5',
  backgroundDark: '#0f230f',

  // Cards y superficies
  surface: '#ffffff',
  surfaceDark: '#1a2e1a',

  // Bordes
  border: '#dae7da',
  borderDark: '#2a3e2a',

  // Texto
  textPrimary: '#111811',
  textSecondary: '#5e8d5e',
  textMuted: '#8fa88f',
  textInverse: '#ffffff',

  // Estados
  error: '#dc2626',
  errorLight: '#fee2e2',
  warning: '#f59e0b',
  warningLight: '#fef3c7',
  success: '#16a34a',

  // Simuladores (solo donde corresponda)
  whatsapp: '#075E54',
  whatsappBg: '#e5ddd5',
  bancoEstado: '#f57a00',
  claveUnica: '#0b4a8e',

  // Genéricos
  white: '#ffffff',
  black: '#000000',
  gray100: '#f3f4f6',
  gray200: '#e5e7eb',
  gray300: '#d1d5db',
  gray400: '#9ca3af',
  gray500: '#6b7280',
  gray600: '#4b5563',
} as const;

export type ColorKey = keyof typeof colors;
