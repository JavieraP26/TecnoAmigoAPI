import { Text, StyleSheet } from 'react-native';
import type { TextStyle } from 'react-native';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize, lineHeight } from '@/constants/typography';

type Variant = 'display' | 'title' | 'subtitle' | 'body' | 'caption' | 'label';
type Color = 'primary' | 'secondary' | 'muted' | 'inverse' | 'error';

interface Props {
  children: React.ReactNode;
  variant?: Variant;
  color?: Color;
  style?: TextStyle;
  numberOfLines?: number;
}

export function StyledText({
  children,
  variant = 'body',
  color = 'primary',
  style,
  numberOfLines,
}: Props) {
  return (
    <Text
      numberOfLines={numberOfLines}
      style={[styles.base, styles[variant], colorStyles[color], style]}
    >
      {children}
    </Text>
  );
}

const styles = StyleSheet.create({
  base: {
    fontFamily: fontFamily.regular,
  },
  display: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['4xl'],
    lineHeight: lineHeight['4xl'],
  },
  title: {
    fontFamily: fontFamily.bold,
    fontSize: fontSize['2xl'],
    lineHeight: lineHeight['2xl'],
  },
  subtitle: {
    fontFamily: fontFamily.semiBold,
    fontSize: fontSize.xl,
    lineHeight: lineHeight.xl,
  },
  body: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.base,
    lineHeight: lineHeight.base,
  },
  caption: {
    fontFamily: fontFamily.regular,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.sm,
  },
  label: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.sm,
    lineHeight: lineHeight.sm,
  },
});

const colorStyles = StyleSheet.create({
  primary: { color: colors.textPrimary },
  secondary: { color: colors.textSecondary },
  muted: { color: colors.textMuted },
  inverse: { color: colors.textInverse },
  error: { color: colors.error },
});
