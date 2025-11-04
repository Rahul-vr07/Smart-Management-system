import { create } from 'zustand';

interface UserStats {
  user_id: string;
  total_points: number;
  items_scanned: number;
  items_recycled: number;
  co2_saved_kg: number;
  badges: string[];
}

interface AppState {
  userStats: UserStats | null;
  isLoading: boolean;
  setUserStats: (stats: UserStats) => void;
  setLoading: (loading: boolean) => void;
  updatePoints: (points: number) => void;
}

export const useStore = create<AppState>((set) => ({
  userStats: null,
  isLoading: false,
  setUserStats: (stats) => set({ userStats: stats }),
  setLoading: (loading) => set({ isLoading: loading }),
  updatePoints: (points) =>
    set((state) => ({
      userStats: state.userStats
        ? { ...state.userStats, total_points: state.userStats.total_points + points }
        : null,
    })),
}));
