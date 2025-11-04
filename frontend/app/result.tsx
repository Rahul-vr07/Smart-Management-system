import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function ResultScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  
  const { classification, category, suggestions, points } = params;

  const getCategoryColor = (cat: string) => {
    if (cat === 'RECYCLE') return '#4CAF50';
    if (cat === 'COMPOST') return '#FF9800';
    return '#757575';
  };

  const getCategoryIcon = (cat: string) => {
    if (cat === 'RECYCLE') return 'recycle';
    if (cat === 'COMPOST') return 'leaf';
    return 'delete';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <MaterialCommunityIcons name="arrow-left" size={24} color="#212121" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Classification Result</Text>
          <View style={{ width: 40 }} />
        </View>

        <View style={styles.successBadge}>
          <MaterialCommunityIcons name="check-circle" size={60} color="#4CAF50" />
          <Text style={styles.successText}>Successfully Classified!</Text>
        </View>

        <View style={styles.pointsCard}>
          <MaterialCommunityIcons name="star" size={32} color="#FF9800" />
          <Text style={styles.pointsText}>+{points} Points Earned!</Text>
        </View>

        <View style={styles.resultCard}>
          <Text style={styles.label}>Classification:</Text>
          <Text style={styles.classification}>{classification}</Text>

          <View style={styles.divider} />

          <Text style={styles.label}>Category:</Text>
          <View
            style={[
              styles.categoryBadge,
              { backgroundColor: getCategoryColor(category as string) },
            ]}
          >
            <MaterialCommunityIcons
              name={getCategoryIcon(category as string) as any}
              size={24}
              color="#FFF"
            />
            <Text style={styles.categoryText}>{category}</Text>
          </View>

          <View style={styles.divider} />

          <Text style={styles.label}>Disposal Suggestions:</Text>
          <Text style={styles.suggestions}>{suggestions}</Text>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/(tabs)')}
        >
          <MaterialCommunityIcons name="camera" size={24} color="#FFF" />
          <Text style={styles.buttonText}>Scan Another Item</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={() => router.push('/(tabs)/bins')}
        >
          <MaterialCommunityIcons name="map-marker" size={24} color="#4CAF50" />
          <Text style={[styles.buttonText, { color: '#4CAF50' }]}>Find Nearest Bin</Text>
        </TouchableOpacity>
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212121',
  },
  successBadge: {
    alignItems: 'center',
    marginBottom: 24,
  },
  successText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginTop: 8,
  },
  pointsCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFF3E0',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    gap: 8,
  },
  pointsText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF9800',
  },
  resultCard: {
    backgroundColor: '#FFF',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  label: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 8,
    fontWeight: '600',
  },
  classification: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 16,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    gap: 8,
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  categoryText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  suggestions: {
    fontSize: 16,
    color: '#424242',
    lineHeight: 24,
  },
  divider: {
    height: 1,
    backgroundColor: '#E0E0E0',
    marginVertical: 16,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    gap: 8,
  },
  secondaryButton: {
    backgroundColor: '#FFF',
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
