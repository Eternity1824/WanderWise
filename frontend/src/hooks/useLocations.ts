import { useEffect } from 'react';
import { useLocationContext } from '../context/LocationContext';
import { locationService } from '../services/api';

export const useLocations = () => {
  const { 
    setLocations, 
    setIsLoading, 
    setError, 
    setMapSettings 
  } = useLocationContext();

  // Fetch locations from API
  const fetchLocations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await locationService.getLocations();
      setLocations(data);

      // If we have locations, center the map on the first one
      if (data.length > 0) {
        setMapSettings((prev) => ({
          ...prev,
          center: {
            lat: data[0].position.lat,
            lng: data[0].position.lng,
          },
        }));
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
      setError('获取地点数据失败，请稍后再试');
    } finally {
      setIsLoading(false);
    }
  };

  // Search locations by query
  const searchLocations = async (query: string) => {
    if (!query.trim()) {
      fetchLocations();
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await locationService.searchLocations(query);
      setLocations(data);
    } catch (error) {
      console.error('Error searching locations:', error);
      setError('搜索地点失败，请稍后再试');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch locations on component mount
  useEffect(() => {
    fetchLocations();
  }, []);

  return { fetchLocations, searchLocations };
}; 