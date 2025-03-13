import React, { useEffect, useState } from 'react';
import { useLocationContext } from '../../context/LocationContext';
import { SortDirection } from '../../types';
import { sortLocationsByDirection, calculateTotalDistance, estimateTravelTime } from '../../utils/locationUtils';
import { routeService } from '../../services/api';

const NavigationPanel: React.FC = () => {
  const {
    locations,
    selectedLocations,
    setSelectedLocations,
    sortDirection,
    setSortDirection,
    currentRoute,
    setCurrentRoute,
    mapSettings,
    isLoading,
    setIsLoading,
    error,
    setError,
  } = useLocationContext();

  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);

  // Get user's current location
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting user location:', error);
          setError('无法获取您的位置，请检查位置权限');
        }
      );
    } else {
      setError('您的浏览器不支持地理定位');
    }
  };

  // Sort locations based on selected direction
  const handleSortLocations = () => {
    if (selectedLocations.length < 2) {
      setError('请至少选择两个地点进行排序');
      return;
    }

    const sortedLocations = sortLocationsByDirection(
      selectedLocations,
      sortDirection,
      userLocation?.lat,
      userLocation?.lng
    );

    setSelectedLocations(sortedLocations);
  };

  // Create a route from selected locations
  const createRoute = async () => {
    if (selectedLocations.length < 2) {
      setError('请至少选择两个地点创建路线');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Try to get route from backend
      const locationIds = selectedLocations.map((loc) => loc.id);
      const route = await routeService.getRoute(locationIds);
      setCurrentRoute(route);
    } catch (error) {
      console.error('Error creating route:', error);
      
      // Fallback: create a simple route without directions
      const totalDistance = calculateTotalDistance(selectedLocations);
      const estimatedTime = estimateTravelTime(totalDistance);
      
      setCurrentRoute({
        id: 'local-route',
        name: '自定义路线',
        locations: selectedLocations,
        totalDistance,
        estimatedTime,
      });
      
      setError('无法从服务器获取路线，已创建简单路线');
    } finally {
      setIsLoading(false);
    }
  };

  // Clear the current route
  const clearRoute = () => {
    setCurrentRoute(null);
  };

  // Clear selected locations
  const clearSelectedLocations = () => {
    setSelectedLocations([]);
    setCurrentRoute(null);
  };

  // Get user location on component mount
  useEffect(() => {
    getUserLocation();
  }, []);

  return (
    <div className="navigation-panel">
      <h2>导航控制面板</h2>
      
      <div className="panel-section">
        <h3>已选择地点 ({selectedLocations.length})</h3>
        {selectedLocations.length > 0 ? (
          <ul className="selected-locations-list">
            {selectedLocations.map((location, index) => (
              <li key={location.id}>
                <span className="location-index">{index + 1}</span>
                <span className="location-name">{location.name}</span>
                <button
                  onClick={() => setSelectedLocations(selectedLocations.filter((loc) => loc.id !== location.id))}
                  className="remove-btn"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p>尚未选择地点，请在地图上选择地点</p>
        )}
        
        {selectedLocations.length > 0 && (
          <button onClick={clearSelectedLocations} className="clear-btn">
            清除所有选择
          </button>
        )}
      </div>

      <div className="panel-section">
        <h3>排序方向</h3>
        <select
          value={sortDirection}
          onChange={(e) => setSortDirection(e.target.value as SortDirection)}
          className="direction-select"
        >
          <option value={SortDirection.NORTH_TO_SOUTH}>从北到南</option>
          <option value={SortDirection.SOUTH_TO_NORTH}>从南到北</option>
          <option value={SortDirection.EAST_TO_WEST}>从东到西</option>
          <option value={SortDirection.WEST_TO_EAST}>从西到东</option>
          <option value={SortDirection.NEAREST_FIRST}>距离最近优先</option>
        </select>
        
        <button
          onClick={handleSortLocations}
          disabled={selectedLocations.length < 2}
          className="sort-btn"
        >
          排序地点
        </button>
      </div>

      <div className="panel-section">
        <h3>路线操作</h3>
        <button
          onClick={createRoute}
          disabled={selectedLocations.length < 2 || isLoading}
          className="route-btn"
        >
          {isLoading ? '创建路线中...' : '创建路线'}
        </button>
        
        {currentRoute && (
          <>
            <div className="route-info">
              <p>
                <strong>总距离:</strong> {currentRoute.totalDistance?.toFixed(2)} 公里
              </p>
              <p>
                <strong>预计时间:</strong> {(currentRoute.estimatedTime || 0) * 60} 分钟
              </p>
            </div>
            <button onClick={clearRoute} className="clear-route-btn">
              清除路线
            </button>
          </>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default NavigationPanel; 