import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function ProfileScreen() {
  const openLink = (url: string) => {
    Linking.openURL(url);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <MaterialCommunityIcons name="account-circle" size={80} color="#4CAF50" />
          </View>
          <Text style={styles.name}>Eco Citizen</Text>
          <Text style={styles.email}>default_user</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About CleanCity</Text>
          <Text style={styles.description}>
            CleanCity is your personal eco-assistant helping you manage waste smartly and contribute to a cleaner environment.
          </Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Features</Text>
          
          <View style={styles.featureItem}>
            <MaterialCommunityIcons name="camera" size={24} color="#4CAF50" />
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>AI Scanner</Text>
              <Text style={styles.featureDesc}>
                Take a picture and get instant waste classification with disposal suggestions
              </Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <MaterialCommunityIcons name="map-marker" size={24} color="#2196F3" />
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Smart Bin Locator</Text>
              <Text style={styles.featureDesc}>
                Find nearby recycling points with real-time bin status and capacity
              </Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <MaterialCommunityIcons name="trophy" size={24} color="#FF9800" />
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Eco Rewards</Text>
              <Text style={styles.featureDesc}>
                Earn points and badges for your recycling efforts and environmental impact
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>App Info</Text>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Version</Text>
            <Text style={styles.infoValue}>1.0.0</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Platform</Text>
            <Text style={styles.infoValue}>Expo</Text>
          </View>
        </View>

        <View style={styles.taglineCard}>
          <MaterialCommunityIcons name="earth" size={40} color="#4CAF50" />
          <Text style={styles.tagline}>Smarter Waste. Cleaner Earth.</Text>
          <Text style={styles.subTagline}>AI + You = A Cleaner Tomorrow</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  content: {
    padding: 16,
  },
  header: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: '#757575',
  },
  section: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 12,
  },
  description: {
    fontSize: 14,
    color: '#616161',
    lineHeight: 22,
  },
  featureItem: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 12,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 4,
  },
  featureDesc: {
    fontSize: 14,
    color: '#757575',
    lineHeight: 20,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  infoLabel: {
    fontSize: 14,
    color: '#757575',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#212121',
  },
  taglineCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
  },
  tagline: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1B5E20',
    marginTop: 12,
    textAlign: 'center',
  },
  subTagline: {
    fontSize: 14,
    color: '#4CAF50',
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
