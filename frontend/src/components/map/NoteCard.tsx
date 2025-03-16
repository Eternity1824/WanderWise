import React, { useState, useEffect } from 'react';
import { PostInfo } from '../../types';
import './NoteCard.css';

interface NoteCardProps {
  post: PostInfo;
  onClick?: () => void;
}

const NoteCard: React.FC<NoteCardProps> = ({ post, onClick }) => {
  const [isCollected, setIsCollected] = useState(post.isCollected || false);

  // 添加调试日志
  useEffect(() => {
    console.log('NoteCard rendered with:', post);
  }, [post]);

  const handleCollectClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsCollected(!isCollected);
    console.log(`${isCollected ? '取消收藏' : '收藏'}笔记:`, post.note_id);
    // 这里可以添加收藏/取消收藏的API调用
  };

  // 处理图片加载错误
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    console.log('Image load error, using default image');
    (e.target as HTMLImageElement).src = '/images/default.jpg';
  };

  return (
    <div className="note-card" onClick={onClick}>
      <div className="note-card-image-container">
        <img 
          src={post.coverImage || '/images/default.jpg'} 
          alt={post.title || '无标题'} 
          className="note-card-image" 
          onError={handleImageError}
        />
      </div>
      <div className="note-card-content">
        <h4 className="note-card-title">{post.title || '无标题'}</h4>
        <div className="note-card-author">{post.nickname || '匿名用户'}</div>
      </div>
      <button 
        className={`note-card-collect-btn ${isCollected ? 'collected' : ''}`}
        onClick={handleCollectClick}
        aria-label={isCollected ? '取消收藏' : '收藏'}
      >
        {isCollected ? (
          <svg viewBox="0 0 24 24" className="heart-icon" style={{ fill: '#ff4d4f', stroke: 'none' }}>
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" className="heart-icon" style={{ fill: 'none', stroke: '#ff4d4f', strokeWidth: 1.5 }}>
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default NoteCard; 