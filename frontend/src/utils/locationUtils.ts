import { Location, SortDirection } from '../types';

// Calculate distance between two points using Haversine formula
export const calculateDistance = (
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number => {
  const R = 6371; // Radius of the earth in km
  const dLat = deg2rad(lat2 - lat1);
  const dLng = deg2rad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c; // Distance in km
  return distance;
};

// Convert degrees to radians
const deg2rad = (deg: number): number => {
  return deg * (Math.PI / 180);
};

// Sort locations based on direction
export const sortLocationsByDirection = (
  locations: Location[],
  direction: SortDirection,
  userLat?: number,
  userLng?: number
): Location[] => {
  const locationsCopy = [...locations];

  switch (direction) {
    case SortDirection.NORTH_TO_SOUTH:
      return locationsCopy.sort((a, b) => b.position.lat - a.position.lat);
    
    case SortDirection.SOUTH_TO_NORTH:
      return locationsCopy.sort((a, b) => a.position.lat - b.position.lat);
    
    case SortDirection.EAST_TO_WEST:
      return locationsCopy.sort((a, b) => b.position.lng - a.position.lng);
    
    case SortDirection.WEST_TO_EAST:
      return locationsCopy.sort((a, b) => a.position.lng - b.position.lng);
    
    case SortDirection.NEAREST_FIRST:
      if (userLat !== undefined && userLng !== undefined) {
        return locationsCopy.sort((a, b) => {
          const distanceA = calculateDistance(userLat, userLng, a.position.lat, a.position.lng);
          const distanceB = calculateDistance(userLat, userLng, b.position.lat, b.position.lng);
          return distanceA - distanceB;
        });
      }
      return locationsCopy;
    
    default:
      return locationsCopy;
  }
};

// Calculate the total distance of a route
export const calculateTotalDistance = (locations: Location[]): number => {
  let totalDistance = 0;
  
  for (let i = 0; i < locations.length - 1; i++) {
    const currentLocation = locations[i];
    const nextLocation = locations[i + 1];
    
    totalDistance += calculateDistance(
      currentLocation.position.lat,
      currentLocation.position.lng,
      nextLocation.position.lat,
      nextLocation.position.lng
    );
  }
  
  return totalDistance;
};

// Estimate travel time based on distance (assuming average speed of 50 km/h)
export const estimateTravelTime = (distanceInKm: number): number => {
  const averageSpeedKmPerHour = 50;
  return distanceInKm / averageSpeedKmPerHour; // Time in hours
}; 