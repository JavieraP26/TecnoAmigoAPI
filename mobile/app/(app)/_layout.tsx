import { StyleSheet, Text, View } from 'react-native';
import { Tabs } from 'expo-router';
import { colors } from '@/constants/colors';
import { fontFamily, fontSize } from '@/constants/typography';
import { tabBarHeight } from '@/constants/spacing';

type IconName = 'home' | 'school' | 'help' | 'person';

const ICONS: Record<IconName, { filled: string; outline: string }> = {
  home: { filled: '⌂', outline: '⌂' },
  school: { filled: '🎓', outline: '🎓' },
  help: { filled: '❓', outline: '❓' },
  person: { filled: '👤', outline: '👤' },
};

interface TabIconProps {
  name: IconName;
  label: string;
  focused: boolean;
}

function TabIcon({ name, label, focused }: TabIconProps) {
  return (
    <View style={tabStyles.container}>
      <Text style={[tabStyles.icon, focused && tabStyles.iconActive]}>
        {ICONS[name].filled}
      </Text>
      <Text style={[tabStyles.label, focused && tabStyles.labelActive]}>
        {label}
      </Text>
    </View>
  );
}

export default function AppLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon name="home" label="Inicio" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="academy"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon name="school" label="Academia" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="simulators"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon name="help" label="Ayuda" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon name="person" label="Perfil" focused={focused} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    height: tabBarHeight + 16,
    paddingBottom: 0,
    backgroundColor: colors.surface,
    borderTopWidth: 2,
    borderTopColor: colors.border,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
  },
});

const tabStyles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    gap: 2,
    height: tabBarHeight,
    width: 70,
  },
  icon: {
    fontSize: 24,
    opacity: 0.4,
  },
  iconActive: {
    opacity: 1,
  },
  label: {
    fontFamily: fontFamily.medium,
    fontSize: fontSize.xs,
    color: colors.gray400,
  },
  labelActive: {
    fontFamily: fontFamily.bold,
    color: colors.primary,
  },
});
