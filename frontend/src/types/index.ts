// Location type definition
export interface Location {
  id: string;
  name: string;
  position: {
    lat: number;
    lng: number;
  };
  description?: string;
  address?: string;
  category?: string;
  rating?: number;
  postInfos?: PostInfo[];
}

// Route type definition
export interface Route {
  id: string;
  name: string;
  locations: Location[];
  totalDistance?: number;
  estimatedTime?: number;
  directions?: any;
}

// Direction type for sorting (North to South, etc.)
export enum SortDirection {
  NORTH_TO_SOUTH = 'NORTH_TO_SOUTH',
  SOUTH_TO_NORTH = 'SOUTH_TO_NORTH',
  EAST_TO_WEST = 'EAST_TO_WEST',
  WEST_TO_EAST = 'WEST_TO_EAST',
  NEAREST_FIRST = 'NEAREST_FIRST',
}

// Map settings type
export interface MapSettings {
  center: {
    lat: number;
    lng: number;
  };
  zoom: number;
}

// API Response types
export interface ApiResponse {
  route?: ApiRouteItem[];
  points?: any[];
  posts?: ApiPost[];
  posts_length?: number;
  mode?: string;
}

export interface ApiRouteItem {
  place_id?: string;
  name?: string;
  latitude?: number;
  longitude?: number;
  formatted_address?: string;
}

export interface ApiPost {
  note_id: string;
  title?: string;
  desc?: string;
  time?: number;
  nickname?: string;
  liked_count?: string;
  locations?: ApiPostLocation[];
  score?: number;
  _score?: number;
}

export interface ApiPostLocation {
  place_id?: string;
  name?: string;
  lat?: number;
  lng?: number;
  formatted_address?: string;
}

// PostInfo type definition
export interface PostInfo {
  note_id: string;
  title?: string;
  nickname?: string;
  likedCount?: string;
  time?: number;
  desc?: string;
  score?: number;
  _score?: number;
} 