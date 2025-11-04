import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { getUserStats, UserStats } from '../../services/api';

export default function RewardsScreen() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getUserStats();
      setStats(data);
    } catch (error) {
      console.log('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBadgeIcon = (badge: string) => {
    if (badge.includes('Warrior')) return 'shield-sword';
    if (badge.includes('Plastic')) return 'bottle-soda';
    return 'medal';
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#4CAF50" />
          <Text style={styles.loadingText}>Loading rewards...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Eco Rewards</Text>
          <Text style={styles.subtitle}>Track your environmental impact</Text>
        </View>

        <View style={styles.pointsCard}>
          <MaterialCommunityIcons name="star" size={48} color="#FF9800" />
          <Text style={styles.pointsLabel}>Total Points</Text>
          <Text style={styles.pointsValue}>{stats?.total_points || 0}</Text>
          <Text style={styles.pointsSubtext}>Keep scanning to earn more!</Text>
        </View>

        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <View style={[styles.statIcon, { backgroundColor: '#E3F2FD' }]}>
              <MaterialCommunityIcons name="camera" size={32} color="#2196F3" />
            </View>
            <Text style={styles.statValue}>{stats?.items_scanned || 0}</Text>
            <Text style={styles.statLabel}>Items Scanned</Text>
          </View>

          <View style={styles.statCard}>
            <View style={[styles.statIcon, { backgroundColor: '#E8F5E9' }]}>
              <MaterialCommunityIcons name="recycle" size={32} color="#4CAF50" />
            </View>
            <Text style={styles.statValue}>{stats?.items_recycled || 0}</Text>
            <Text style={styles.statLabel}>Items Recycled</Text>
          </View>

          <View style={styles.statCard}>
            <View style={[styles.statIcon, { backgroundColor: '#FFF3E0' }]}>
              <MaterialCommunityIcons name="leaf" size={32} color="#FF9800" />
            </View>
            <Text style={styles.statValue}>{stats?.co2_saved_kg.toFixed(1) || 0}</Text>
            <Text style={styles.statLabel}>CO₂ Saved (kg)</Text>
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <MaterialCommunityIcons name="trophy" size={24} color="#FF9800" />
            <Text style={styles.sectionTitle}>Your Badges</Text>
          </View>

          {stats?.badges && stats.badges.length > 0 ? (
            <View style={styles.badgesContainer}>
              {stats.badges.map((badge, index) => (
                <View key={index} style={styles.badge}>
                  <MaterialCommunityIcons
                    name={getBadgeIcon(badge) as any}
                    size={40}
                    color="#FF9800"
                  />
                  <Text style={styles.badgeName}>{badge}</Text>
                </View>
              ))}
            </View>
          ) : (
            <View style={styles.emptyBadges}>
              <MaterialCommunityIcons name="trophy-outline" size={48} color="#BDBDBD" />
              <Text style={styles.emptyText}>No badges earned yet</Text>
              <Text style={styles.emptySubtext}>Scan 10 items to earn your first badge!</Text>
            </View>
          )}
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <MaterialCommunityIcons name="target" size={24} color="#4CAF50" />
            <Text style={styles.sectionTitle}>Available Badges</Text>
          </View>

          <View style={styles.achievementsContainer}>
            <View style={styles.achievement}>
              <MaterialCommunityIcons
                name="shield-sword"
                size={32}
                color={stats?.items_scanned >= 10 ? '#FF9800' : '#BDBDBD'}
              />
              <View style={styles.achievementInfo}>
                <Text style={styles.achievementName}>Eco Warrior</Text>
                <Text style={styles.achievementDesc}>Scan 10 items</Text>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      {
                        width: `${Math.min(((stats?.items_scanned || 0) / 10) * 100, 100)}%`,
                      },
                    ]}
                  />
                </View>
              </View>
              <Text style={styles.progressText}>
                {stats?.items_scanned || 0}/10
              </Text>
            </View>

            <View style={styles.achievement}>
              <MaterialCommunityIcons
                name="bottle-soda"
                size={32}
                color={stats?.items_recycled >= 5 ? '#FF9800' : '#BDBDBD'}
              />
              <View style={styles.achievementInfo}>
                <Text style={styles.achievementName}>Plastic Reducer</Text>
                <Text style={styles.achievementDesc}>Recycle 5 items</Text>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      {
                        width: `${Math.min(((stats?.items_recycled || 0) / 5) * 100, 100)}%`,
                      },
                    ]}
                  />
                </View>
              </View>
              <Text style={styles.progressText}>
                {stats?.items_recycled || 0}/5
              </Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.refreshButton} onPress={loadStats}>
          <MaterialCommunityIcons name="refresh" size={20} color="#FFF" />
          <Text style={styles.refreshButtonText}>Refresh Stats</Text>
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#212121',
  },
  subtitle: {
    fontSize: 16,
    color: '#757575',
    marginTop: 4,
  },
  pointsCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  pointsLabel: {
    fontSize: 16,
    color: '#757575',
    marginTop: 12,
  },
  pointsValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FF9800',
    marginTop: 8,
  },
  pointsSubtext: {
    fontSize: 14,
    color: '#9E9E9E',
    marginTop: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  statIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#757575',
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    gap: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212121',
  },
  badgesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  badge: {
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFF3E0',
    borderRadius: 12,
    minWidth: 100,
  },
  badgeName: {
    marginTop: 8,
    fontSize: 12,
    fontWeight: '600',
    color: '#E65100',
    textAlign: 'center',
  },
  emptyBadges: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#9E9E9E',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#BDBDBD',
    marginTop: 8,
  },
  achievementsContainer: {
    gap: 16,
  },
  achievement: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  achievementInfo: {
    flex: 1,
  },
  achievementName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#212121',
    marginBottom: 4,
  },
  achievementDesc: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#757575',
  },
  refreshButton: {
    flexDirection: 'row',
    backgroundColor: '#4CAF50',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  refreshButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#757575',
  },
});
