import React, { useCallback, useState } from 'react';
import { GoogleMap, useJsApiLoader } from '@react-google-maps/api';
import { useLocationContext } from '../../context/LocationContext';
import LocationMarker from './LocationMarker';
import RouteDisplay from './RouteDisplay';

// Map container styles
const containerStyle = {
  width: '100%',
  height: '100vh',
};

// Default map options
const defaultOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: true,
  mapTypeControl: true,
};

const MapContainer: React.FC = () => {
  const { 
    locations, 
    selectedLocations, 
    currentRoute, 
    mapSettings,
    setMapSettings
  } = useLocationContext();
  
  const [map, setMap] = useState<google.maps.Map | null>(null);

  // Load Google Maps API
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    libraries: ['places'],
  });

  // Map load callback
  const onLoad = useCallback((map: google.maps.Map) => {
    setMap(map);
  }, []);

  // Map unload callback
  const onUnmount = useCallback(() => {
    setMap(null);
  }, []);

  // Handle map center change
  const onCenterChanged = () => {
    if (map) {
      const newCenter = map.getCenter();
      if (newCenter) {
        setMapSettings({
          ...mapSettings,
          center: {
            lat: newCenter.lat(),
            lng: newCenter.lng(),
          },
        });
      }
    }
  };

  // Handle map zoom change
  const onZoomChanged = () => {
    if (map) {
      const newZoom = map.getZoom();
      if (newZoom) {
        setMapSettings({
          ...mapSettings,
          zoom: newZoom,
        });
      }
    }
  };

  // Show loading error
  if (loadError) {
    return <div>地图加载错误，请检查您的API密钥</div>;
  }

  // Show loading indicator
  if (!isLoaded) {
    return <div>加载地图中...</div>;
  }

  return (
    <div className="map-container">
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={mapSettings.center}
        zoom={mapSettings.zoom}
        options={defaultOptions}
        onLoad={onLoad}
        onUnmount={onUnmount}
        onCenterChanged={onCenterChanged}
        onZoomChanged={onZoomChanged}
      >
        {/* Render location markers */}
        {locations.map((location) => (
          <LocationMarker
            key={location.id}
            location={location}
            isSelected={selectedLocations.some((selected) => selected.id === location.id)}
          />
        ))}

        {/* Render route if available */}
        {currentRoute && <RouteDisplay route={currentRoute} />}
      </GoogleMap>
    </div>
  );
};

export default MapContainer; 