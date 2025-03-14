import React, { useState } from 'react';
import { Location } from '../../types';
import './LocationCard.css';

interface LocationCardProps {
  location: Location;
  isCompact: boolean; // 是否显示紧凑模式（小比例尺）
  onClose: () => void;
}

const LocationCard: React.FC<LocationCardProps> = ({ location, isCompact, onClose }) => {
  // 添加当前图片索引状态
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  
  // 获取当前星期几（0-6，0表示星期日）
  const today = new Date().getDay();
  const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const todayKey = daysOfWeek[today] as keyof typeof location.openingHours;
  
  // 获取今天的营业时间
  const todayHours = location.openingHours?.[todayKey] || '信息未提供';
  
  // 获取所有图片URL
  const photos = location.photos && location.photos.length > 0 
    ? location.photos 
    : ['https://via.placeholder.com/150?text=No+Image'];
  
  // 获取当前显示的图片
  const currentPhoto = photos[currentPhotoIndex];
  
  // 切换到下一张图片
  const nextPhoto = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡
    if (currentPhotoIndex < photos.length - 1) {
      setCurrentPhotoIndex(currentPhotoIndex + 1);
    } else {
      setCurrentPhotoIndex(0); // 循环到第一张
    }
  };
  
  // 切换到上一张图片
  const prevPhoto = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止事件冒泡
    if (currentPhotoIndex > 0) {
      setCurrentPhotoIndex(currentPhotoIndex - 1);
    } else {
      setCurrentPhotoIndex(photos.length - 1); // 循环到最后一张
    }
  };
  
  // 紧凑模式（小比例尺）
  if (isCompact) {
    return (
      <div className="location-card location-card-compact">
        <div className="card-image-container">
          <img 
            src={currentPhoto} 
            alt={location.name} 
            className="card-image"
            onError={(e) => {
              // 图片加载失败时使用默认图片
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=No+Image';
            }}
          />
          {photos.length > 1 && (
            <>
              <button className="photo-nav-button prev-button" onClick={prevPhoto}>❮</button>
              <button className="photo-nav-button next-button" onClick={nextPhoto}>❯</button>
              <div className="photo-indicator">{currentPhotoIndex + 1}/{photos.length}</div>
            </>
          )}
        </div>
        <div className="card-content">
          <h3 className="card-title">{location.name}</h3>
        </div>
      </div>
    );
  }
  
  // 详细模式（大比例尺）
  return (
    <div className="location-card location-card-detailed">
      <div className="card-image-container">
        <img 
          src={currentPhoto} 
          alt={location.name} 
          className="card-image"
          onError={(e) => {
            // 图片加载失败时使用默认图片
            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x180?text=No+Image';
          }}
        />
        {photos.length > 1 && (
          <>
            <button className="photo-nav-button prev-button" onClick={prevPhoto}>❮</button>
            <button className="photo-nav-button next-button" onClick={nextPhoto}>❯</button>
            <div className="photo-indicator">{currentPhotoIndex + 1}/{photos.length}</div>
          </>
        )}
      </div>
      <div className="card-content">
        <h3 className="card-title">{location.name}</h3>
        {location.address && <p className="card-address">{location.address}</p>}
        
        <div className="card-details">
          {location.rating !== undefined && location.rating > 0 && (
            <div className="card-rating">
              <span className="rating-value">{location.rating.toFixed(1)}</span>
              <span className="rating-stars">
                {'★'.repeat(Math.floor(location.rating))}
                {'☆'.repeat(5 - Math.floor(location.rating))}
              </span>
            </div>
          )}
          
          <div className="card-hours">
            <strong>今日营业时间:</strong> {todayHours}
          </div>
          
          {location.phone && (
            <div className="card-phone">
              <strong>电话:</strong> <a href={`tel:${location.phone}`}>{location.phone}</a>
            </div>
          )}
          
          {location.website && (
            <div className="card-website">
              <strong>网站:</strong> <a href={location.website} target="_blank" rel="noopener noreferrer">访问官网</a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LocationCard; 