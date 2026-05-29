import { StyleSheet, Text, View } from 'react-native';
import { colors } from '@/constants/colors';
import { radius } from '@/constants/spacing';
import { fontFamily, fontSize } from '@/constants/typography';

type Variant = 'primary' | 'success' | 'warning' | 'error' | 'neutral';

interface Props {
  label: string;
  variant?: Variant;
  count?: number;
}

export function Badge({ label, variant = 'primary', count }: Props) {
  return (
    <View style={[styles.badge, variantStyles[variant]]}>
      <Text style={[styles.text, textStyles[variant]]}>
        {count !== undefined ? `${label} ${count}` : label}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radius.full,
    alignSelf: 'flex-start',
  },
  text: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.xs,
  },
});

const variantStyles = StyleSheet.create({
  primary: { backgroundColor: colors.primaryLight },
  success: { backgroundColor: colors.success + '20' },
  warning: { backgroundColor: colors.warningLight },
  error: { backgroundColor: colors.errorLight },
  neutral: { backgroundColor: colors.gray100 },
});

const textStyles = StyleSheet.create({
  primary: { color: colors.primary },
  success: { color: colors.success },
  warning: { color: colors.warning },
  error: { color: colors.error },
  neutral: { color: colors.gray600 },
});
