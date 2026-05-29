import { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@/components/ui/Button';
import api from '@/lib/api';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize, lineHeight } from '@/constants/typography';
import { inputHeight, radius, spacing } from '@/constants/spacing';

export default function RegisterScreen() {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);

  const digits = phone.replace(/\D/g, '');
  const isValid = digits.length === 9 && digits.startsWith('9');

  async function handleSend() {
    if (!isValid) return;
    try {
      setLoading(true);
      await api.post('/auth/send-sms', { phone: `+56${digits}` });
      router.push({ pathname: '/(auth)/verify', params: { phone: `+56${digits}` } });
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? 'No se pudo enviar el SMS. Intenta de nuevo.';
      Alert.alert('Error', msg);
    } finally {
      setLoading(false);
    }
  }

  function formatDisplay(text: string) {
    const d = text.replace(/\D/g, '').slice(0, 9);
    if (d.length <= 1) return d;
    if (d.length <= 5) return `${d[0]} ${d.slice(1)}`;
    return `${d[0]} ${d.slice(1, 5)} ${d.slice(5)}`;
  }

  return (
    <SafeAreaView style={styles.screen}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={{ flex: 1 }}
      >
        <ScrollView
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <Pressable onPress={() => router.back()} style={styles.backBtn}>
            <Text style={styles.backArrow}>←</Text>
          </Pressable>

          <View style={styles.header}>
            <Text style={styles.title}>Crear tu cuenta</Text>
            <Text style={styles.subtitle}>Ingresa tu número de celular</Text>
          </View>

          <View style={styles.phoneBox}>
            <View style={styles.inputRow}>
              <View style={styles.prefix}>
                <Text style={styles.prefixText}>🇨🇱 +56</Text>
              </View>
              <View style={styles.divider} />
              <TextInput
                value={formatDisplay(phone)}
                onChangeText={(t) => setPhone(t.replace(/\D/g, '').slice(0, 9))}
                placeholder="9 1234 5678"
                placeholderTextColor={colors.textMuted}
                keyboardType="phone-pad"
                style={styles.phoneInput}
                maxLength={12}
              />
            </View>
            <Text style={styles.hint}>
              Recibirás un SMS con un código de 6 dígitos
            </Text>
          </View>

          <View style={styles.action}>
            <Button
              label="Enviar código SMS"
              onPress={handleSend}
              loading={loading}
              disabled={!isValid}
            />
          </View>

          <Text style={styles.legal}>
            Al registrarte, aceptas nuestros{' '}
            <Text style={styles.legalLink}>Términos de Servicio</Text> y{' '}
            <Text style={styles.legalLink}>Política de Privacidad</Text>
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing['2xl'],
  },
  backBtn: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.sm,
  },
  backArrow: {
    fontSize: 24,
    color: colors.textPrimary,
  },
  header: {
    paddingTop: spacing.lg,
    paddingBottom: spacing['2xl'],
  },
  title: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['5xl'],
    lineHeight: lineHeight['5xl'],
    color: colors.textPrimary,
  },
  subtitle: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.lg,
    color: colors.gray500,
    marginTop: spacing.sm,
  },
  phoneBox: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 2,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.sm,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    height: inputHeight,
    gap: spacing.sm,
  },
  prefix: {
    paddingHorizontal: spacing.sm,
  },
  prefixText: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.xl,
    color: colors.textPrimary,
  },
  divider: {
    width: 1,
    height: 24,
    backgroundColor: colors.border,
  },
  phoneInput: {
    flex: 1,
    fontFamily: fontFamily.medium,
    fontSize: fontSize.xl,
    color: colors.textPrimary,
  },
  hint: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.sm,
    color: colors.textMuted,
  },
  action: {
    marginTop: spacing.xl,
  },
  legal: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.sm,
    color: colors.gray500,
    textAlign: 'center',
    marginTop: spacing.xl,
    lineHeight: lineHeight.sm * 1.5,
  },
  legalLink: {
    color: colors.primary,
    fontFamily: fontFamily.medium,
  },
});
