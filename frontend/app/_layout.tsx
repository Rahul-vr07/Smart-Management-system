import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useEffect } from 'react';
import { seedData } from '../services/api';

export default function RootLayout() {
  useEffect(() => {
    // Seed database with sample data on app start
    seedData().catch((err) => console.log('Seed data:', err.message));
  }, []);

  return (
    <SafeAreaProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="scanner" />
        <Stack.Screen name="result" />
      </Stack>
    </SafeAreaProvider>
  );
}
