import { StyleSheet, View } from 'react-native';
import { colors } from '@/constants/colors';
import { radius } from '@/constants/spacing';

interface Props {
  progress: number; // 0 to 1
  height?: number;
  color?: string;
  trackColor?: string;
}

export function ProgressBar({
  progress,
  height = 12,
  color = colors.primary,
  trackColor = colors.primaryLight,
}: Props) {
  const clampedProgress = Math.min(1, Math.max(0, progress));

  return (
    <View style={[styles.track, { height, backgroundColor: trackColor }]}>
      <View
        style={[
          styles.fill,
          {
            width: `${clampedProgress * 100}%`,
            height,
            backgroundColor: color,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    width: '100%',
    borderRadius: radius.full,
    overflow: 'hidden',
  },
  fill: {
    borderRadius: radius.full,
  },
});
