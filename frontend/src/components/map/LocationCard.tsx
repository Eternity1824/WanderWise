import React, { useState } from 'react';
import { Location } from '../../types';
import './LocationCard.css';

interface LocationCardProps {
  location: Location;
  isCompact?: boolean;
  onClose?: () => void;
}

const LocationCard: React.FC<LocationCardProps> = ({ location, isCompact = false, onClose }) => {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  
  // 获取当前星期几，用于显示今天的营业时间
  const today = new Date().getDay();
  const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'] as const;
  const todayKey = daysOfWeek[today] as keyof typeof location.openingHours;
  
  const todayHours = location.openingHours?.[todayKey] || '未知';
  
  // 图片导航
  const handlePrevPhoto = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (location.photos && location.photos.length > 1) {
      setCurrentPhotoIndex((prev) => (prev === 0 ? location.photos!.length - 1 : prev - 1));
    }
  };
  
  const handleNextPhoto = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (location.photos && location.photos.length > 1) {
      setCurrentPhotoIndex((prev) => (prev === location.photos!.length - 1 ? 0 : prev + 1));
    }
  };
  
  // 获取当前显示的图片URL
  const currentPhotoUrl = location.photos && location.photos.length > 0
    ? location.photos[currentPhotoIndex]
    : 'https://via.placeholder.com/300x200?text=No+Image';
  
  const cardClassName = isCompact ? 'location-card location-card-mini' : 'location-card location-card-detailed';
  const titleClassName = isCompact ? 'card-title mini' : 'card-title';
  const contentClassName = isCompact ? 'card-content mini' : 'card-content';
  
  return (
    <div className={cardClassName} onClick={(e) => e.stopPropagation()}>
      <div className="card-image-container">
        <img 
          src={currentPhotoUrl} 
          alt={location.name} 
          className="card-image"
        />
        
        {!isCompact && location.photos && location.photos.length > 1 && (
          <>
            <button 
              className="photo-nav-button prev-button rectangle" 
              onClick={handlePrevPhoto}
            >
              ‹
            </button>
            <button 
              className="photo-nav-button next-button rectangle" 
              onClick={handleNextPhoto}
            >
              ›
            </button>
            <div className="photo-indicator">
              {currentPhotoIndex + 1} / {location.photos.length}
            </div>
          </>
        )}
      </div>
      
      <div className={contentClassName}>
        <h3 className={titleClassName}>{location.name}</h3>
        
        {!isCompact && (
          <>
            <p className="card-address">{location.address}</p>
            
            <div className="card-details">
              {location.rating !== undefined && (
                <div className="card-rating">
                  <span className="rating-value">{location.rating.toFixed(1)}</span>
                  <span className="rating-stars">
                    {'★'.repeat(Math.floor(location.rating))}
                    {location.rating % 1 >= 0.5 ? '½' : ''}
                    {'☆'.repeat(5 - Math.ceil(location.rating))}
                  </span>
                </div>
              )}
              
              {location.openingHours && (
                <div className="card-hours">
                  <strong>今日营业时间:</strong> {todayHours}
                </div>
              )}
              
              {location.phone && (
                <div className="card-phone">
                  <strong>电话:</strong> <a href={`tel:${location.phone}`}>{location.phone}</a>
                </div>
              )}
              
              {location.website && (
                <div className="card-website">
                  <strong>网站:</strong> <a href={location.website} target="_blank" rel="noopener noreferrer">访问网站</a>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LocationCard; 