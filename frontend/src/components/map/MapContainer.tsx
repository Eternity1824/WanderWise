import React, { useCallback, useState, useRef, useEffect } from 'react';
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

// 定义libraries为常量，避免重新加载
const libraries = ['places'];

const MapContainer: React.FC = () => {
  const { 
    locations, 
    selectedLocations, 
    currentRoute, 
    mapSettings,
    setMapSettings
  } = useLocationContext();
  
  const [map, setMap] = useState<google.maps.Map | null>(null);
  
  // 使用ref来跟踪上一次的中心和缩放级别，避免不必要的更新
  const lastCenterRef = useRef(mapSettings.center);
  const lastZoomRef = useRef(mapSettings.zoom);
  
  // 使用ref来防止过于频繁的更新
  const centerChangedTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const zoomChangedTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Load Google Maps API
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  // Map load callback
  const onLoad = useCallback((map: google.maps.Map) => {
    setMap(map);
  }, []);

  // Map unload callback
  const onUnmount = useCallback(() => {
    setMap(null);
  }, []);

  // Handle map center change with debounce
  const onCenterChanged = useCallback(() => {
    if (!map) return;
    
    // 清除之前的timeout
    if (centerChangedTimeoutRef.current) {
      clearTimeout(centerChangedTimeoutRef.current);
    }
    
    // 设置新的timeout，延迟更新状态
    centerChangedTimeoutRef.current = setTimeout(() => {
      const newCenter = map.getCenter();
      if (newCenter) {
        const centerLat = newCenter.lat();
        const centerLng = newCenter.lng();
        
        // 只有当中心点发生显著变化时才更新
        if (
          Math.abs(centerLat - lastCenterRef.current.lat) > 0.0001 ||
          Math.abs(centerLng - lastCenterRef.current.lng) > 0.0001
        ) {
          const updatedCenter = {
            lat: centerLat,
            lng: centerLng,
          };
          
          lastCenterRef.current = updatedCenter;
          
          setMapSettings(prev => ({
            ...prev,
            center: updatedCenter,
          }));
        }
      }
    }, 300); // 300ms的防抖延迟
  }, [map, setMapSettings]);

  // Handle map zoom change with debounce
  const onZoomChanged = useCallback(() => {
    if (!map) return;
    
    // 清除之前的timeout
    if (zoomChangedTimeoutRef.current) {
      clearTimeout(zoomChangedTimeoutRef.current);
    }
    
    // 设置新的timeout，延迟更新状态
    zoomChangedTimeoutRef.current = setTimeout(() => {
      const newZoom = map.getZoom();
      if (newZoom && newZoom !== lastZoomRef.current) {
        lastZoomRef.current = newZoom;
        
        setMapSettings(prev => ({
          ...prev,
          zoom: newZoom,
        }));
      }
    }, 300); // 300ms的防抖延迟
  }, [map, setMapSettings]);
  
  // 清理timeout
  useEffect(() => {
    return () => {
      if (centerChangedTimeoutRef.current) {
        clearTimeout(centerChangedTimeoutRef.current);
      }
      if (zoomChangedTimeoutRef.current) {
        clearTimeout(zoomChangedTimeoutRef.current);
      }
    };
  }, []);

  // Show loading error
  if (loadError) {
    return <div>地图加载错误，请检查您的API密钥: {loadError.message}</div>;
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
            key={`location-${location.id}`}
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