import { useEffect } from 'react';
import { useLocationContext } from '../context/LocationContext';
import { locationService } from '../services/api';
import { Location, MapSettings, ApiResponse, ApiRouteItem, ApiPost, ApiPostLocation, PostInfo, PathPoint, ApiPhoto, ApiPlace } from '../types';

export const useLocations = () => {
  const { 
    setLocations, 
    setIsLoading, 
    setError, 
    setMapSettings,
    setPathPoints
  } = useLocationContext();

  // 解析营业时间文本为对象
  const parseWeekdayText = (weekdayText?: string[]): Location['openingHours'] => {
    if (!weekdayText || weekdayText.length === 0) return undefined;
    
    const openingHours: Location['openingHours'] = {};
    
    weekdayText.forEach(text => {
      const match = text.match(/^(\w+):\s(.+)$/);
      if (match) {
        const day = match[1].toLowerCase();
        const hours = match[2];
        
        switch (day) {
          case 'monday':
            openingHours.monday = hours;
            break;
          case 'tuesday':
            openingHours.tuesday = hours;
            break;
          case 'wednesday':
            openingHours.wednesday = hours;
            break;
          case 'thursday':
            openingHours.thursday = hours;
            break;
          case 'friday':
            openingHours.friday = hours;
            break;
          case 'saturday':
            openingHours.saturday = hours;
            break;
          case 'sunday':
            openingHours.sunday = hours;
            break;
        }
      }
    });
    
    return openingHours;
  };
  
  // 提取照片URL
  const extractPhotoUrls = (photos?: ApiPhoto[]): string[] => {
    if (!photos || photos.length === 0) return [];
    return photos.map(photo => photo.photo_url);
  };

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
          // 使用name和坐标生成唯一ID
          const locationId = item.place_id || `route-${item.name}-${item.latitude}-${item.longitude}`;
          
          // 如果这个地点已经存在，更新它
          if (locationMap.has(locationId)) {
            // 不需要更新，因为route没有帖子信息
          } else {
            // 提取照片URL
            const photoUrls = extractPhotoUrls(item.photos);
            
            // 解析营业时间
            const openingHours = parseWeekdayText(item.weekday_text);
            
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
              rating: item.rating || 0,
              postInfos: [], // 初始化空数组
              // 添加新字段
              photos: photoUrls,
              phone: item.formatted_phone_number,
              website: item.website,
              openingHours: openingHours
            });
          }
        });
      }
      
      // 处理places数组（周边推荐的地点）
      if (apiResponse.places && Array.isArray(apiResponse.places)) {
        console.log('Processing places data:', apiResponse.places);
        apiResponse.places.forEach((placeItem: ApiPlace) => {
          const place = placeItem.place;
          if (!place || !place.place_id) return;
          
          const locationId = place.place_id;
          
          // 如果这个地点已经存在，不重复添加
          if (locationMap.has(locationId)) {
            return;
          }
          
          // 提取照片URL
          const photoUrls = extractPhotoUrls(place.photos);
          
          // 解析营业时间
          const openingHours = parseWeekdayText(place.weekday_text);
          
          // 获取位置坐标
          const position = {
            lat: place.geometry?.location?.lat || place.location?.lat || 0,
            lng: place.geometry?.location?.lng || place.location?.lon || 0,
          };
          
          // 确定地点类型（美食或景点）
          let placeType: 'food' | 'attraction' | undefined;
          
          // 首先检查 place 对象中的 source_keyword 字段
          if (place.source_keyword) {
            const placeKeyword = place.source_keyword;
            console.log(`Place ${place.name} has source_keyword in place object:`, placeKeyword);
            
            if (placeKeyword.includes('美食')) {
              placeType = 'food';
              console.log(`${place.name} is set as FOOD type from place.source_keyword: ${placeKeyword}`);
            } else if (placeKeyword.includes('景点')) {
              placeType = 'attraction';
              console.log(`${place.name} is set as ATTRACTION type from place.source_keyword: ${placeKeyword}`);
            }
          }
          
          // 如果 place 对象中没有找到匹配的 source_keyword，则检查 notes 数组
          if (!placeType && placeItem.notes && placeItem.notes.length > 0) {
            // 打印每个地点的 notes 和 source_keyword 信息
            console.log(`Place ${place.name} has ${placeItem.notes.length} notes`);
            
            // 检查每个 note 的 source_keyword
            for (const note of placeItem.notes) {
              const keyword = note.source_keyword || '';
              console.log(`Note source_keyword for ${place.name}:`, keyword);
              
              // 更精确地检查关键词
              if (keyword.includes('美食')) {
                placeType = 'food';
                console.log(`${place.name} is set as FOOD type from note.source_keyword: ${keyword}`);
                break; // 一旦找到匹配项就停止循环
              } else if (keyword.includes('景点')) {
                placeType = 'attraction';
                console.log(`${place.name} is set as ATTRACTION type from note.source_keyword: ${keyword}`);
                break; // 一旦找到匹配项就停止循环
              }
            }
          }
          
          // 如果没有找到匹配的关键词，设置默认值
          if (!placeType) {
            // 默认设置为景点
            placeType = 'attraction';
            console.log(`${place.name} has no recognized type in source_keywords, defaulting to ATTRACTION`);
          }
          
          // 创建新的地点
          locationMap.set(locationId, {
            id: locationId,
            name: place.name || '未命名地点',
            position: position,
            description: '',
            address: place.formatted_address || '',
            category: 'place', // 使用'place'类别来区分
            placeType: placeType, // 设置地点类型
            rating: place.rating || 0,
            postInfos: [], // 初始化空数组
            // 添加新字段
            photos: photoUrls,
            phone: place.formatted_phone_number,
            website: place.website,
            openingHours: openingHours
          });
          
          // 打印最终创建的地点信息
          console.log(`Created location for ${place.name}:`, {
            category: 'place',
            placeType: placeType
          });
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
                  postInfos: [postInfo],
                  // 添加图片
                  photos: location.photos || []
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