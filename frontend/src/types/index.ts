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
}

// Route type definition
export interface Route {
  id: string;
  name: string;
  locations: Location[];
  totalDistance?: number;
  estimatedTime?: number;
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
  zoom: number;
  center: {
    lat: number;
    lng: number;
  };
} 