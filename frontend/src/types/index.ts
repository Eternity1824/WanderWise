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
  photos?: string[];  // 图片URL数组
  phone?: string;     // 电话号码
  website?: string;   // 官网地址
  openingHours?: {    // 营业时间
    monday?: string;
    tuesday?: string;
    wednesday?: string;
    thursday?: string;
    friday?: string;
    saturday?: string;
    sunday?: string;
  };
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

// Path point type definition
export interface PathPoint {
  latitude: number;
  longitude: number;
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
  points?: PathPoint[];
  posts?: ApiPost[];
  posts_length?: number;
  mode?: string;
}

// 照片类型
export interface ApiPhoto {
  height: number;
  width: number;
  photo_url: string;
}

export interface ApiRouteItem {
  place_id?: string;
  name?: string;
  latitude?: number;
  longitude?: number;
  formatted_address?: string;
  formatted_phone_number?: string;  // 更新为后端返回的字段名
  rating?: number;
  url?: string;                     // Google Maps URL
  website?: string;
  weekday_text?: string[];         // 营业时间数组
  photos?: ApiPhoto[];             // 照片对象数组
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
  photos?: string[];  // 图片URL数组
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