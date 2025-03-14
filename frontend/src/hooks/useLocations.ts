import { useEffect } from 'react';
import { useLocationContext } from '../context/LocationContext';
import { locationService } from '../services/api';
import { Location, MapSettings, ApiResponse, ApiRouteItem, ApiPost, ApiPostLocation, PostInfo, PathPoint } from '../types';

export const useLocations = () => {
  const { 
    setLocations, 
    setIsLoading, 
    setError, 
    setMapSettings,
    setPathPoints
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
        setMapSettings(prev => ({
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
      console.log('Searching for:', query);
      const response = await locationService.searchLocations(query);
      console.log('API Response:', response);
      
      // 创建一个Map来存储按place_id分组的位置
      const locationMap = new Map<string, Location>();
      
      // 检查响应格式并提取位置数据
      const apiResponse = response as ApiResponse;
      
      // 处理路径点数据
      if (apiResponse.points && Array.isArray(apiResponse.points)) {
        console.log('Processing path points:', apiResponse.points.length);
        setPathPoints(apiResponse.points);
      } else {
        // 如果没有路径点，清空路径点数组
        setPathPoints([]);
      }
      
      // 处理route数组（主要景点）
      if (apiResponse.route && Array.isArray(apiResponse.route)) {
        console.log('Processing route data:', apiResponse.route);
        apiResponse.route.forEach((item: ApiRouteItem, index: number) => {
          if (!item.place_id) return;
          
          const locationId = item.place_id;
          
          // 如果这个地点已经存在，更新它
          if (locationMap.has(locationId)) {
            // 不需要更新，因为route没有帖子信息
          } else {
            // 创建新的地点
            locationMap.set(locationId, {
              id: locationId,
              name: item.name || '未命名地点',
              position: {
                lat: item.latitude || 0,
                lng: item.longitude || 0,
              },
              description: '',
              address: item.formatted_address || '',
              category: 'route',
              rating: 0,
              postInfos: [] // 初始化空数组
            });
          }
        });
      }
      
      // 处理posts数组（用户分享的地点）
      if (apiResponse.posts && Array.isArray(apiResponse.posts)) {
        console.log('Processing posts data:', apiResponse.posts);
        
        // 先按_score排序帖子
        const sortedPosts = [...apiResponse.posts].sort((a, b) => {
          return (b._score || 0) - (a._score || 0);
        });
        
        sortedPosts.forEach((post: ApiPost) => {
          // 检查post是否有locations数组
          if (post.locations && Array.isArray(post.locations)) {
            post.locations.forEach((location: ApiPostLocation) => {
              if (!location.place_id) return;
              
              const locationId = location.place_id;
              
              // 创建帖子信息对象
              const postInfo: PostInfo = {
                note_id: post.note_id,
                title: post.title,
                nickname: post.nickname,
                likedCount: post.liked_count,
                time: post.time,
                desc: post.desc,
                score: post.score,
                _score: post._score
              };
              
              // 如果这个地点已经存在，添加帖子信息
              if (locationMap.has(locationId)) {
                const existingLocation = locationMap.get(locationId)!;
                existingLocation.postInfos = existingLocation.postInfos || [];
                existingLocation.postInfos.push(postInfo);
                
                // 确保帖子按_score排序
                existingLocation.postInfos.sort((a, b) => {
                  return (b._score || 0) - (a._score || 0);
                });
              } else {
                // 创建新的地点
                locationMap.set(locationId, {
                  id: locationId,
                  name: location.name || post.title || '未命名地点',
                  position: {
                    lat: location.lat || 0,
                    lng: location.lng || 0,
                  },
                  description: post.desc || '',
                  address: location.formatted_address || '',
                  category: 'post',
                  rating: 0,
                  postInfos: [postInfo]
                });
              }
            });
          }
        });
      }
      
      // 将Map转换为数组
      const formattedData = Array.from(locationMap.values());
      
      console.log('Formatted data:', formattedData);
      setLocations(formattedData);
      
      // 如果有位置数据，将地图中心设置到第一个位置
      if (formattedData.length > 0) {
        setMapSettings(prev => ({
          ...prev,
          center: {
            lat: formattedData[0].position.lat,
            lng: formattedData[0].position.lng,
          },
          zoom: 12, // 设置适当的缩放级别
        }));
      }
    } catch (error) {
      console.error('Error searching locations:', error);
      setError('搜索地点失败，请稍后再试');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch locations on component mount
  useEffect(() => {
    // 初始化时不自动获取位置，等待用户搜索
    // fetchLocations();
  }, []);

  return { fetchLocations, searchLocations };
}; 