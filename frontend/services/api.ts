import axios from 'axios';
import Constants from 'expo-constants';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:3000';
const API_URL = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface WasteClassificationResponse {
  id: string;
  classification: string;
  category: string;
  suggestions: string;
  points_awarded: number;
}

export interface BinLocation {
  id: string;
  name: string;
  type: string;
  latitude: number;
  longitude: number;
  address: string;
  status: string;
  capacity: number;
  timings: string;
}

export interface UserStats {
  user_id: string;
  total_points: number;
  items_scanned: number;
  items_recycled: number;
  co2_saved_kg: number;
  badges: string[];
}

export const classifyWaste = async (imageBase64: string): Promise<WasteClassificationResponse> => {
  const response = await api.post('/classify-waste', {
    image_base64: imageBase64,
    user_id: 'default_user',
  });
  return response.data;
};

export const getBins = async (): Promise<BinLocation[]> => {
  const response = await api.get('/bins');
  return response.data;
};

export const getUserStats = async (userId: string = 'default_user'): Promise<UserStats> => {
  const response = await api.get(`/user-stats/${userId}`);
  return response.data;
};

export const seedData = async () => {
  const response = await api.post('/seed-data');
  return response.data;
};

export const createReport = async (data: {
  location: string;
  latitude: number;
  longitude: number;
  description: string;
  image_base64?: string;
}) => {
  const response = await api.post('/reports', {
    ...data,
    user_id: 'default_user',
  });
  return response.data;
};

export default api;
