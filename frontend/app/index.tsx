import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  StatusBar,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function Welcome() {
  const router = useRouter();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.gradient}>
        <View style={styles.content}>
          <View style={styles.iconContainer}>
            <MaterialCommunityIcons name="earth" size={80} color="#4CAF50" />
          </View>
          
          <Text style={styles.title}>CleanCity</Text>
          <Text style={styles.subtitle}>Your Personal Eco-Assistant</Text>
          
          <View style={styles.features}>
            <View style={styles.feature}>
              <MaterialCommunityIcons name="camera" size={32} color="#4CAF50" />
              <Text style={styles.featureText}>AI Waste Scanner</Text>
            </View>
            <View style={styles.feature}>
              <MaterialCommunityIcons name="map-marker" size={32} color="#2196F3" />
              <Text style={styles.featureText}>Smart Bin Locator</Text>
            </View>
            <View style={styles.feature}>
              <MaterialCommunityIcons name="trophy" size={32} color="#FF9800" />
              <Text style={styles.featureText}>Eco Rewards</Text>
            </View>
          </View>
          
          <TouchableOpacity
            style={styles.button}
            onPress={() => router.replace('/(tabs)')
            }
          >
            <Text style={styles.buttonText}>Get Started</Text>
            <MaterialCommunityIcons name="arrow-right" size={24} color="#FFF" />
          </TouchableOpacity>
          
          <Text style={styles.tagline}>Snap. Predict. Dispose Smartly.</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A1F0A',
  },
  gradient: {
    flex: 1,
    backgroundColor: 'linear-gradient(135deg, #0A1F0A 0%, #1B5E20 100%)',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#A5D6A7',
    marginBottom: 48,
  },
  features: {
    width: '100%',
    marginBottom: 48,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  featureText: {
    color: '#FFF',
    fontSize: 16,
    marginLeft: 16,
    fontWeight: '600',
  },
  button: {
    flexDirection: 'row',
    backgroundColor: '#4CAF50',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#4CAF50',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginRight: 8,
  },
  tagline: {
    color: '#81C784',
    fontSize: 14,
    fontStyle: 'italic',
  },
});
