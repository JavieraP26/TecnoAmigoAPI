import { useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize } from '@/constants/typography';
import { radius, spacing } from '@/constants/spacing';

export default function SplashScreen() {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;
    if (isAuthenticated) {
      router.replace('/(app)');
    } else {
      router.replace('/(auth)/onboarding');
    }
  }, [isAuthenticated, isLoading]);

  return (
    <View style={styles.container}>
      <View style={styles.logoBox}>
        <Text style={styles.logoIcon}>🤝</Text>
      </View>
      <Text style={styles.brand}>TecnoAmigo</Text>
      <Text style={styles.tagline}>Aprende tecnología a tu ritmo</Text>

      <View style={styles.dots}>
        <View style={[styles.dot, { opacity: 0.2 }]} />
        <View style={[styles.dot, { opacity: 0.4 }]} />
        <View style={[styles.dot, { opacity: 0.6 }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  logoBox: {
    width: 120,
    height: 140,
    borderRadius: radius.lg,
    backgroundColor: colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
    borderWidth: 2,
    borderColor: colors.primary + '30',
  },
  logoIcon: {
    fontSize: 72,
  },
  brand: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['4xl'],
    color: colors.primary,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  tagline: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.base,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  dots: {
    position: 'absolute',
    bottom: spacing['2xl'],
    flexDirection: 'row',
    gap: spacing.sm,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: radius.full,
    backgroundColor: colors.primary,
  },
});
