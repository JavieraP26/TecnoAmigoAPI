import { StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize } from '@/constants/typography';
import { spacing } from '@/constants/spacing';

export default function AcademyScreen() {
  return (
    <SafeAreaView style={styles.screen} edges={['top', 'left', 'right']}>
      <View style={styles.center}>
        <Text style={styles.emoji}>🎓</Text>
        <Text style={styles.title}>Academia</Text>
        <Text style={styles.subtitle}>Próximamente</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: spacing.md },
  emoji: { fontSize: 64 },
  title: { fontFamily: fontFamily.bold, fontSize: fontSize['2xl'], color: colors.textPrimary },
  subtitle: { fontFamily: fontFamily.regular, fontSize: fontSize.base, color: colors.textSecondary },
});
