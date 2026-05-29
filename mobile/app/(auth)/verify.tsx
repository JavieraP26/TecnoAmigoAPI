import { useRef, useState, useEffect } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@/components/ui/Button';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize, lineHeight } from '@/constants/typography';
import { radius, spacing } from '@/constants/spacing';

const CODE_LENGTH = 6;
const RESEND_TIMEOUT = 60;

export default function VerifyScreen() {
  const { phone } = useLocalSearchParams<{ phone: string }>();
  const { login } = useAuth();

  const [digits, setDigits] = useState<string[]>(Array(CODE_LENGTH).fill(''));
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(RESEND_TIMEOUT);
  const inputRefs = useRef<(TextInput | null)[]>([]);

  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const code = digits.join('');
  const isComplete = code.length === CODE_LENGTH;

  function handleDigit(index: number, value: string) {
    const d = value.replace(/\D/g, '').slice(-1);
    const next = [...digits];
    next[index] = d;
    setDigits(next);
    if (d && index < CODE_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  }

  function handleKeyPress(index: number, key: string) {
    if (key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }

  async function handleVerify() {
    if (!isComplete) return;
    try {
      setLoading(true);
      const { data } = await api.post('/auth/verify-otp', {
        phone,
        code,
      });
      await login(data.access_token, data.refresh_token);
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'Código incorrecto. Intenta de nuevo.';
      Alert.alert('Error', msg);
      setDigits(Array(CODE_LENGTH).fill(''));
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    if (countdown > 0) return;
    try {
      await api.post('/auth/send-sms', { phone });
      setCountdown(RESEND_TIMEOUT);
      setDigits(Array(CODE_LENGTH).fill(''));
      inputRefs.current[0]?.focus();
    } catch {
      Alert.alert('Error', 'No se pudo reenviar el SMS. Intenta de nuevo.');
    }
  }

  const formattedPhone = phone?.replace('+56', '+56 ') ?? '';

  return (
    <SafeAreaView style={styles.screen}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={{ flex: 1 }}
      >
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backArrow}>←</Text>
        </Pressable>

        <View style={styles.body}>
          <View style={styles.iconBox}>
            <Text style={styles.iconEmoji}>💬</Text>
          </View>

          <Text style={styles.title}>Ingresa el código</Text>
          <Text style={styles.subtitle}>
            Enviamos un código a{' '}
            <Text style={styles.phoneHighlight}>{formattedPhone}</Text>
          </Text>

          <View style={styles.otpRow}>
            {digits.map((d, i) => (
              <TextInput
                key={i}
                ref={(r) => { inputRefs.current[i] = r; }}
                value={d}
                onChangeText={(v) => handleDigit(i, v)}
                onKeyPress={({ nativeEvent }) => handleKeyPress(i, nativeEvent.key)}
                keyboardType="number-pad"
                maxLength={1}
                selectTextOnFocus
                style={[styles.otpBox, d ? styles.otpFilled : null]}
              />
            ))}
          </View>

          <View style={styles.action}>
            <Button
              label="Verificar"
              onPress={handleVerify}
              loading={loading}
              disabled={!isComplete}
            />
          </View>

          <View style={styles.resendRow}>
            {countdown > 0 ? (
              <Text style={styles.countdown}>
                Reenviar en {countdown}s
              </Text>
            ) : (
              <Pressable onPress={handleResend}>
                <Text style={styles.resendLink}>No recibí el código</Text>
              </Pressable>
            )}
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  backBtn: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: spacing.md,
    marginTop: spacing.sm,
  },
  backArrow: {
    fontSize: 24,
    color: colors.textPrimary,
  },
  body: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xl,
  },
  iconBox: {
    width: 100,
    height: 100,
    borderRadius: radius.full,
    backgroundColor: colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  iconEmoji: {
    fontSize: 52,
  },
  title: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['2xl'],
    lineHeight: lineHeight['2xl'],
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.base,
    color: colors.gray500,
    textAlign: 'center',
    paddingHorizontal: spacing.md,
  },
  phoneHighlight: {
    fontFamily: fontFamily.semiBold,
    color: colors.textPrimary,
  },
  otpRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.xl,
    marginBottom: spacing.xl,
  },
  otpBox: {
    width: 50,
    height: 60,
    borderRadius: radius.md,
    borderWidth: 2,
    borderColor: colors.border,
    textAlign: 'center',
    fontFamily: fontFamily.bold,
    fontSize: fontSize.xl,
    color: colors.textPrimary,
    backgroundColor: colors.surface,
  },
  otpFilled: {
    borderColor: colors.primary,
  },
  action: {
    width: '100%',
    marginBottom: spacing.lg,
  },
  resendRow: {
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  countdown: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.base,
    color: colors.gray500,
  },
  resendLink: {
    fontFamily: fontFamily.semiBold,
    fontSize: fontSize.base,
    color: colors.primary,
  },
});
