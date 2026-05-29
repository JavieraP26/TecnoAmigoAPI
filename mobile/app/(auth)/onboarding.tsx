import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@/components/ui/Button';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize, lineHeight } from '@/constants/typography';
import { radius, spacing } from '@/constants/spacing';

const FEATURES = [
  {
    emoji: '💬',
    bg: colors.primaryLight,
    title: 'WhatsApp',
    subtitle: 'Mensajes con la familia',
  },
  {
    emoji: '🏦',
    bg: '#e3f2fd',
    title: 'Banco',
    subtitle: 'Tus finanzas seguras',
  },
  {
    emoji: '📋',
    bg: '#fff3e0',
    title: 'Trámites',
    subtitle: 'Trámites digitales',
  },
] as const;

export default function OnboardingScreen() {
  return (
    <SafeAreaView style={styles.screen}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={styles.title}>Bienvenido a TecnoAmigo</Text>
          <Text style={styles.subtitle}>Aprende tecnología a tu ritmo</Text>
        </View>

        <View style={styles.cards}>
          {FEATURES.map((f) => (
            <View key={f.title} style={styles.card}>
              <View style={[styles.iconBox, { backgroundColor: f.bg }]}>
                <Text style={styles.emoji}>{f.emoji}</Text>
              </View>
              <View style={styles.cardText}>
                <Text style={styles.cardTitle}>{f.title}</Text>
                <Text style={styles.cardSubtitle}>{f.subtitle}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={styles.cta}>
          <Button label="Comenzar" onPress={() => router.push('/(auth)/register')} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  content: {
    flexGrow: 1,
    paddingBottom: spacing.xl,
  },
  header: {
    paddingHorizontal: spacing.lg,
    paddingTop: spacing['2xl'],
    paddingBottom: spacing.md,
    alignItems: 'center',
  },
  title: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['5xl'],
    lineHeight: lineHeight['5xl'],
    color: colors.textPrimary,
    textAlign: 'center',
  },
  subtitle: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.lg,
    lineHeight: lineHeight.lg,
    color: colors.textPrimary,
    textAlign: 'center',
    marginTop: spacing.md,
  },
  cards: {
    padding: spacing.lg,
    gap: spacing.lg,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 3,
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  iconBox: {
    width: 64,
    height: 64,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emoji: {
    fontSize: 32,
  },
  cardText: {
    flex: 1,
    marginLeft: spacing.md,
  },
  cardTitle: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.xl,
    color: colors.textPrimary,
  },
  cardSubtitle: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.base,
    color: colors.textSecondary,
    marginTop: 4,
  },
  cta: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
  },
});
