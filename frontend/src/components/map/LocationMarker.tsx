import React, { useState, useEffect } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { Location, PostInfo } from '../../types';
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
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const { selectedLocations, setSelectedLocations, mapSettings } = useLocationContext();

  // 根据地图缩放级别决定是否显示详细卡片
  const isDetailedView = mapSettings.zoom >= ZOOM_THRESHOLD;

  // 当缩放级别变化时，重置帖子索引
  useEffect(() => {
    setCurrentPostIndex(0);
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
    // 重置帖子索引
    setCurrentPostIndex(0);
  };

  // Close info window
  const closeInfoWindow = () => {
    setIsInfoOpen(false);
  };

  // 根据类别选择不同的图标
  const getMarkerIcon = () => {
    // 添加日志输出
    console.log(`Getting marker icon for ${location.name}:`, {
      category: location.category,
      placeType: location.placeType,
      isSelected: isSelected
    });

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
        console.log(`${location.name} using BLUE icon for food`);
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
        console.log(`${location.name} using GREEN icon for attraction or default`);
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

  // 格式化时间
  const formatTime = (timestamp: number | undefined) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString();
  };

  // 显示下一个帖子
  const showNextPost = () => {
    if (location.postInfos && currentPostIndex < location.postInfos.length - 1) {
      setCurrentPostIndex(currentPostIndex + 1);
    }
  };

  // 显示上一个帖子
  const showPrevPost = () => {
    if (location.postInfos && currentPostIndex > 0) {
      setCurrentPostIndex(currentPostIndex - 1);
    }
  };

  // 获取当前帖子
  const getCurrentPost = (): PostInfo | undefined => {
    if (location.postInfos && location.postInfos.length > 0) {
      return location.postInfos[currentPostIndex];
    }
    return undefined;
  };

  // 获取帖子数量
  const getPostCount = (): number => {
    return location.postInfos?.length || 0;
  };

  const currentPost = getCurrentPost();
  const postCount = getPostCount();

  // 获取动画设置
  const getAnimation = () => {
    return location.category === 'route' || location.category === 'place'
      ? window.google.maps.Animation.DROP 
      : undefined;
  };

  // 渲染地点卡片或帖子信息
  const renderInfoContent = () => {
    // 如果是route或place类别的地点，显示地点卡片
    if (location.category === 'route' || location.category === 'place') {
      return (
        <LocationCard 
          location={location} 
          isCompact={!isDetailedView} 
          onClose={closeInfoWindow} 
        />
      );
    }
    
    // 获取类别显示文本
    const getCategoryText = () => {
      if (location.category === 'route') return '主要景点';
      if (location.category === 'place') {
        return location.placeType === 'food' ? '美食' : '景点';
      }
      return '用户分享';
    };
    
    // 如果是post类别的地点，显示帖子信息
    return (
      <div className="info-window">
        <h3>{location.name}</h3>
        {location.description && <p>{location.description}</p>}
        {location.address && <p><strong>地址:</strong> {location.address}</p>}
        <p><strong>类别:</strong> {getCategoryText()}</p>
        {location.rating && location.rating > 0 && (
          <p>
            <strong>评分:</strong> {location.rating} / 5
            <span className="stars">
              {'★'.repeat(Math.floor(location.rating))}
              {'☆'.repeat(5 - Math.floor(location.rating))}
            </span>
          </p>
        )}
        
        {/* 显示帖子信息 */}
        {postCount > 0 && currentPost && (
          <div className="post-info">
            <hr />
            <div className="post-navigation">
              <h4>用户分享 ({currentPostIndex + 1}/{postCount})</h4>
              <div className="post-nav-buttons">
                <button 
                  onClick={(e) => { e.stopPropagation(); showPrevPost(); }} 
                  disabled={currentPostIndex === 0}
                  className="post-nav-button"
                >
                  ◀
                </button>
                <button 
                  onClick={(e) => { e.stopPropagation(); showNextPost(); }} 
                  disabled={currentPostIndex === postCount - 1}
                  className="post-nav-button"
                >
                  ▶
                </button>
              </div>
            </div>
            
            {currentPost.title && <p><strong>标题:</strong> {currentPost.title}</p>}
            {currentPost.nickname && <p><strong>用户:</strong> {currentPost.nickname}</p>}
            {currentPost.likedCount && <p><strong>点赞:</strong> {currentPost.likedCount}</p>}
            {currentPost.time && <p><strong>时间:</strong> {formatTime(currentPost.time)}</p>}
            {currentPost.desc && (
              <div className="post-desc">
                <strong>描述:</strong>
                <p className="desc-text">{currentPost.desc}</p>
              </div>
            )}
          </div>
        )}
        
        <div className="info-actions">
          <button onClick={toggleSelection}>
            {isSelected ? '取消选择' : '选择此地点'}
          </button>
        </div>
      </div>
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