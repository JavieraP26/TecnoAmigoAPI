import { useEffect, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@/components/ui/Card';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize, lineHeight } from '@/constants/typography';
import { radius, spacing } from '@/constants/spacing';

interface DashboardData {
  user: { name: string };
  progress: { current_lesson?: { title: string; progress: number; remaining_minutes: number } };
  journey: { achievements_unlocked: number; achievements_total: number };
}

export default function DashboardScreen() {
  const { logout } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    Promise.all([
      api.get('/users/me'),
      api.get('/progress/welcome'),
      api.get('/journey/status'),
    ])
      .then(([user, progress, journey]) => {
        setData({
          user: user.data,
          progress: progress.data,
          journey: journey.data,
        });
      })
      .catch(() => {});
  }, []);

  const name = data?.user?.name ?? '';
  const lesson = data?.progress?.current_lesson;
  const unlocked = data?.journey?.achievements_unlocked ?? 0;
  const total = data?.journey?.achievements_total ?? 14;

  return (
    <SafeAreaView style={styles.screen} edges={['top', 'left', 'right']}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {name ? name[0].toUpperCase() : '?'}
            </Text>
          </View>
          <Text style={styles.greeting} numberOfLines={1}>
            Hola{name ? `, ${name.split(' ')[0]}` : ''}
          </Text>
        </View>
        <Pressable style={styles.notifBtn}>
          <Text style={styles.notifIcon}>🔔</Text>
        </Pressable>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Continúa tu lección */}
        {lesson && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Continúa tu lección</Text>
            <Card style={styles.lessonCard} padding="lg">
              <Text style={styles.lessonTitle} numberOfLines={2}>
                {lesson.title}
              </Text>
              <View style={styles.progressRow}>
                <Text style={styles.progressPct}>
                  {Math.round(lesson.progress * 100)}% completado
                </Text>
                <Text style={styles.progressTime}>
                  {lesson.remaining_minutes} min restantes
                </Text>
              </View>
              <ProgressBar progress={lesson.progress} />
              <Pressable
                style={styles.continueBtn}
                onPress={() => router.push('/(app)/academy')}
              >
                <Text style={styles.continueBtnText}>▶ Continuar</Text>
              </Pressable>
            </Card>
          </View>
        )}

        {/* Practica en Simuladores */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Practica en Simuladores</Text>
          <View style={styles.simGrid}>
            <Pressable
              style={styles.simCard}
              onPress={() => router.push('/(app)/simulators')}
            >
              <View style={[styles.simIcon, { backgroundColor: '#e3f2fd' }]}>
                <Text style={styles.simEmoji}>🏦</Text>
              </View>
              <Text style={styles.simLabel}>BancoEstado</Text>
            </Pressable>
            <Pressable
              style={styles.simCard}
              onPress={() => router.push('/(app)/simulators')}
            >
              <View style={[styles.simIcon, { backgroundColor: colors.primaryLight }]}>
                <Text style={styles.simEmoji}>💬</Text>
              </View>
              <Text style={styles.simLabel}>WhatsApp</Text>
            </Pressable>
          </View>
        </View>

        {/* Tus Logros */}
        <View style={styles.section}>
          <View style={styles.sectionRow}>
            <Text style={styles.sectionTitle}>Tus Logros</Text>
            <Pressable onPress={() => router.push('/(app)/profile')}>
              <Text style={styles.seeAll}>Ver todos ›</Text>
            </Pressable>
          </View>
          <View style={styles.statsGrid}>
            <Card style={styles.statCard} padding="md">
              <Text style={styles.statValue}>{unlocked}</Text>
              <Text style={styles.statLabel}>logros{'\n'}desbloqueados</Text>
            </Card>
            <Card style={styles.statCard} padding="md">
              <Text style={styles.statValue}>{total - unlocked}</Text>
              <Text style={styles.statLabel}>logros{'\n'}por descubrir</Text>
            </Card>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 2,
    borderBottomColor: colors.border,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: radius.full,
    backgroundColor: colors.primaryMid,
    borderWidth: 2,
    borderColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.xl,
    color: colors.primary,
  },
  greeting: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['2xl'],
    color: colors.textPrimary,
  },
  notifBtn: {
    width: 48,
    height: 48,
    borderRadius: radius.full,
    backgroundColor: colors.gray100,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.gray200,
  },
  notifIcon: {
    fontSize: 22,
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingBottom: spacing.xl,
  },
  section: {
    padding: spacing.lg,
    paddingBottom: 0,
  },
  sectionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.xl,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  seeAll: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.base,
    color: colors.primary,
  },
  lessonCard: {
    gap: spacing.md,
  },
  lessonTitle: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['2xl'],
    lineHeight: lineHeight['2xl'],
    color: colors.textPrimary,
  },
  progressRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  progressPct: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.lg,
    color: colors.primary,
  },
  progressTime: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.base,
    color: colors.gray500,
  },
  continueBtn: {
    height: 56,
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  continueBtnText: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.xl,
    color: colors.textInverse,
  },
  simGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  simCard: {
    flex: 1,
    height: 144,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 2,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
  },
  simIcon: {
    width: 56,
    height: 56,
    borderRadius: radius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  simEmoji: {
    fontSize: 28,
  },
  simLabel: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize.lg,
    color: colors.textPrimary,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  statCard: {
    flex: 1,
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  statValue: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['4xl'],
    color: colors.textPrimary,
  },
  statLabel: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.base,
    color: colors.gray500,
    lineHeight: lineHeight.base,
  },
});
