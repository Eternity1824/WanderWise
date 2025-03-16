import React, { useState, useEffect } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { Location } from '../../types';
import { useLocationContext } from '../../context/LocationContext';
import LocationCard from './LocationCard';

interface LocationMarkerProps {
  location: Location;
  isSelected: boolean;
}

// 定义缩放级别阈值，大于等于此值时显示详细卡片
const ZOOM_THRESHOLD = 15;

const LocationMarker: React.FC<LocationMarkerProps> = ({ location, isSelected }) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const { selectedLocations, setSelectedLocations, mapSettings } = useLocationContext();

  // 根据地图缩放级别决定是否显示详细卡片
  const isDetailedView = mapSettings.zoom >= ZOOM_THRESHOLD;

  // 当缩放级别变化时，重置帖子索引
  useEffect(() => {
    // 不再需要重置索引
  }, [isDetailedView]);

  // Toggle location selection
  const toggleSelection = () => {
    if (isSelected) {
      setSelectedLocations(selectedLocations.filter((loc) => loc.id !== location.id));
    } else {
      setSelectedLocations([...selectedLocations, location]);
    }
  };

  // Toggle info window
  const toggleInfoWindow = () => {
    setIsInfoOpen(!isInfoOpen);
    
    // 简化调试信息
    console.log('地点名称:', location.name);
    console.log('地点ID:', location.id);
    console.log('是否有笔记:', !!(location.postInfos && location.postInfos.length > 0));
    if (location.postInfos && location.postInfos.length > 0) {
      console.log('笔记数量:', location.postInfos.length);
    }
    console.log('当前缩放级别:', mapSettings.zoom);
    console.log('是否为详细视图:', isDetailedView);
  };

  // Close info window
  const closeInfoWindow = () => {
    setIsInfoOpen(false);
  };

  // 根据类别选择不同的图标
  const getMarkerIcon = () => {
    if (isSelected) {
      return {
        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        scaledSize: new window.google.maps.Size(40, 40),
      };
    }
    
    // 根据类别选择不同颜色的图标
    if (location.category === 'route') {
      return {
        url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
        scaledSize: new window.google.maps.Size(40, 40),
      };
    } else if (location.category === 'place') {
      // 根据 placeType 选择不同颜色
      if (location.placeType === 'food') {
        // 美食用蓝色圆点
        return {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: '#1E88E5', // 蓝色
          fillOpacity: 1,
          strokeColor: '#ffffff', // 白色边框
          strokeWeight: 2,
        };
      } else {
        // 景点用绿色圆点（默认）
        return {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: '#00b300', // 深绿色
          fillOpacity: 1,
          strokeColor: '#ffffff', // 白色边框
          strokeWeight: 2,
        };
      }
    } else if (location.category === 'post') {
      // 为post类别使用更小的绿色圆点
      return {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: 8,
        fillColor: '#4CAF50', // 浅绿色
        fillOpacity: 1,
        strokeColor: '#ffffff', // 白色边框
        strokeWeight: 2,
      };
    }
    
    return {
      url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
      scaledSize: new window.google.maps.Size(40, 40),
    };
  };

  // 获取动画设置
  const getAnimation = () => {
    return location.category === 'route' || location.category === 'place'
      ? window.google.maps.Animation.DROP 
      : undefined;
  };

  // 渲染信息窗口内容
  const renderInfoContent = () => {
    // 如果是详细视图模式且有笔记数据，显示地点卡片和笔记列表
    if (isDetailedView && location.postInfos && location.postInfos.length > 0) {
      console.log('显示笔记数据:', location.postInfos);
      
      return (
        <div className="info-window-content">
          <LocationCard 
            location={location} 
            isCompact={false} 
            onClose={() => setIsInfoOpen(false)}
          />
        </div>
      );
    }
    
    // 默认显示地点卡片
    return (
      <LocationCard 
        location={location} 
        isCompact={!isDetailedView} 
        onClose={() => setIsInfoOpen(false)}
      />
    );
  };

  return (
    <>
      <Marker
        // 使用更复杂的唯一key
        key={`marker-${location.id}-${isSelected ? 'selected' : 'normal'}`}
        position={location.position}
        onClick={toggleInfoWindow}
        onDblClick={toggleSelection}
        icon={getMarkerIcon()}
        animation={getAnimation()}
        title={location.name}
        // 禁用优化以避免重复渲染问题
        options={{
          optimized: false
        }}
      />

      {isInfoOpen && (
        <InfoWindow
          position={location.position}
          onCloseClick={closeInfoWindow}
          options={{
            pixelOffset: new window.google.maps.Size(0, -5),
            maxWidth: isDetailedView ? 320 : 180,
            disableAutoPan: false
          }}
        >
          {renderInfoContent()}
        </InfoWindow>
      )}
    </>
  );
};

export default LocationMarker; 