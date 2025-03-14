import React, { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { Location, PostInfo } from '../../types';
import { useLocationContext } from '../../context/LocationContext';

interface LocationMarkerProps {
  location: Location;
  isSelected: boolean;
}

const LocationMarker: React.FC<LocationMarkerProps> = ({ location, isSelected }) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const { selectedLocations, setSelectedLocations } = useLocationContext();

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
    } else if (location.category === 'post') {
      // 为post类别使用更小的绿色圆点
      return {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: 8,
        fillColor: '#00b300', // 深绿色
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
    return location.category === 'route' 
      ? window.google.maps.Animation.DROP 
      : undefined;
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
        >
          <div className="info-window">
            <h3>{location.name}</h3>
            {location.description && <p>{location.description}</p>}
            {location.address && <p><strong>地址:</strong> {location.address}</p>}
            {location.category && <p><strong>类别:</strong> {location.category === 'route' ? '主要景点' : '用户分享'}</p>}
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
        </InfoWindow>
      )}
    </>
  );
};

export default LocationMarker; 