import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import * as Location from 'expo-location';
import { getBins, BinLocation } from '../../services/api';

export default function BinsScreen() {
  const [bins, setBins] = useState<BinLocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);

  useEffect(() => {
    loadBins();
    requestLocationPermission();
  }, []);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const loc = await Location.getCurrentPositionAsync({});
        setLocation(loc);
      }
    } catch (error) {
      console.log('Location permission error:', error);
    }
  };

  const loadBins = async () => {
    try {
      setLoading(true);
      const data = await getBins();
      setBins(data);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load bin locations');
    } finally {
      setLoading(false);
    }
  };

  const calculateDistance = (lat: number, lon: number) => {
    if (!location) return null;
    const R = 6371; // Earth's radius in km
    const dLat = ((lat - location.coords.latitude) * Math.PI) / 180;
    const dLon = ((lon - location.coords.longitude) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((location.coords.latitude * Math.PI) / 180) *
        Math.cos((lat * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    return distance.toFixed(1);
  };

  const getBinIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'recycling':
        return 'recycle';
      case 'compost':
        return 'leaf';
      case 'e-waste':
        return 'laptop';
      default:
        return 'delete';
    }
  };

  const getBinColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'recycling':
        return '#4CAF50';
      case 'compost':
        return '#FF9800';
      case 'e-waste':
        return '#9C27B0';
      default:
        return '#757575';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return '#4CAF50';
      case 'full':
        return '#F44336';
      case 'maintenance':
        return '#FF9800';
      default:
        return '#757575';
    }
  };

  const renderBin = ({ item }: { item: BinLocation }) => {
    const distance = calculateDistance(item.latitude, item.longitude);

    return (
      <TouchableOpacity style={styles.binCard}>
        <View style={styles.binHeader}>
          <View
            style={[
              styles.binIconContainer,
              { backgroundColor: getBinColor(item.type) + '20' },
            ]}
          >
            <MaterialCommunityIcons
              name={getBinIcon(item.type) as any}
              size={32}
              color={getBinColor(item.type)}
            />
          </View>
          <View style={styles.binInfo}>
            <Text style={styles.binName}>{item.name}</Text>
            <Text style={styles.binType}>{item.type.toUpperCase()}</Text>
          </View>
          {distance && (
            <View style={styles.distanceContainer}>
              <MaterialCommunityIcons name="map-marker-distance" size={16} color="#757575" />
              <Text style={styles.distanceText}>{distance} km</Text>
            </View>
          )}
        </View>

        <View style={styles.binDetails}>
          <View style={styles.detail}>
            <MaterialCommunityIcons name="map-marker" size={18} color="#757575" />
            <Text style={styles.detailText}>{item.address}</Text>
          </View>
          <View style={styles.detail}>
            <MaterialCommunityIcons name="clock" size={18} color="#757575" />
            <Text style={styles.detailText}>{item.timings}</Text>
          </View>
          <View style={styles.statusRow}>
            <View style={styles.detail}>
              <MaterialCommunityIcons
                name="checkbox-marked-circle"
                size={18}
                color={getStatusColor(item.status)}
              />
              <Text style={[styles.detailText, { color: getStatusColor(item.status) }]}>
                {item.status.toUpperCase()}
              </Text>
            </View>
            <View style={styles.capacityContainer}>
              <View style={styles.capacityBar}>
                <View
                  style={[
                    styles.capacityFill,
                    {
                      width: `${item.capacity}%`,
                      backgroundColor: item.capacity > 80 ? '#F44336' : '#4CAF50',
                    },
                  ]}
                />
              </View>
              <Text style={styles.capacityText}>{item.capacity}%</Text>
            </View>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>Loading bin locations...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Smart Bin Locator</Text>
          <Text style={styles.subtitle}>Find recycling points near you</Text>
        </View>
        <TouchableOpacity style={styles.refreshButton} onPress={loadBins}>
          <MaterialCommunityIcons name="refresh" size={24} color="#4CAF50" />
        </TouchableOpacity>
      </View>

      {!location && (
        <View style={styles.locationAlert}>
          <MaterialCommunityIcons name="alert-circle" size={20} color="#FF9800" />
          <Text style={styles.alertText}>
            Enable location to see distances to bins
          </Text>
        </View>
      )}

      <FlatList
        data={bins}
        renderItem={renderBin}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <MaterialCommunityIcons name="map-marker-off" size={64} color="#BDBDBD" />
            <Text style={styles.emptyText}>No bin locations found</Text>
            <TouchableOpacity style={styles.refreshButtonLarge} onPress={loadBins}>
              <Text style={styles.refreshButtonText}>Refresh</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212121',
  },
  subtitle: {
    fontSize: 14,
    color: '#757575',
    marginTop: 4,
  },
  refreshButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  locationAlert: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    padding: 12,
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 8,
    gap: 8,
  },
  alertText: {
    flex: 1,
    fontSize: 14,
    color: '#E65100',
  },
  listContent: {
    padding: 16,
  },
  binCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  binHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  binIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  binInfo: {
    flex: 1,
    marginLeft: 12,
  },
  binName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 4,
  },
  binType: {
    fontSize: 12,
    color: '#757575',
    fontWeight: '600',
  },
  distanceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  distanceText: {
    fontSize: 14,
    color: '#757575',
    fontWeight: '600',
  },
  binDetails: {
    gap: 8,
  },
  detail: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  detailText: {
    fontSize: 14,
    color: '#424242',
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  capacityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  capacityBar: {
    width: 80,
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  capacityFill: {
    height: '100%',
    borderRadius: 4,
  },
  capacityText: {
    fontSize: 12,
    color: '#757575',
    fontWeight: '600',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#757575',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 16,
    color: '#9E9E9E',
    marginTop: 16,
    marginBottom: 24,
  },
  refreshButtonLarge: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  refreshButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
