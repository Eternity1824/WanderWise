import React from 'react';
import { Polyline, DirectionsRenderer } from '@react-google-maps/api';
import { Route } from '../../types';

interface RouteDisplayProps {
  route: Route;
}

const RouteDisplay: React.FC<RouteDisplayProps> = ({ route }) => {
  // If we have directions from the Google Maps Directions API
  if ('directions' in route && route.directions) {
    return <DirectionsRenderer directions={route.directions} />;
  }

  // Otherwise, create a simple polyline between locations
  const path = route.locations.map((location) => ({
    lat: location.position.lat,
    lng: location.position.lng,
  }));

  return (
    <Polyline
      path={path}
      options={{
        strokeColor: '#0088FF',
        strokeOpacity: 0.8,
        strokeWeight: 5,
        geodesic: true,
      }}
    />
  );
};

export default RouteDisplay; 