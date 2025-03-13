import axios from 'axios';
import { Location, Route } from '../types';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions for locations
export const locationService = {
  // Get all locations
  getLocations: async (): Promise<Location[]> => {
    try {
      const response = await api.get<Location[]>('/locations');
      return response.data;
    } catch (error) {
      console.error('Error fetching locations:', error);
      throw error;
    }
  },

  // Get a single location by ID
  getLocationById: async (id: string): Promise<Location> => {
    try {
      const response = await api.get<Location>(`/locations/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching location with id ${id}:`, error);
      throw error;
    }
  },

  // Search locations by query
  searchLocations: async (query: string): Promise<Location[]> => {
    try {
      const response = await api.get<Location[]>(`/locations/search`, {
        params: { query },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching locations:', error);
      throw error;
    }
  },
};

// API functions for routes
export const routeService = {
  // Get route between locations
  getRoute: async (locationIds: string[]): Promise<Route> => {
    try {
      const response = await api.post<Route>('/routes', { locationIds });
      return response.data;
    } catch (error) {
      console.error('Error fetching route:', error);
      throw error;
    }
  },
};

export default api; 