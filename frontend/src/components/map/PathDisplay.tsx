import React from 'react';
import { Polyline } from '@react-google-maps/api';

// 定义路径点的类型
interface PathPoint {
  latitude: number;
  longitude: number;
}

interface PathDisplayProps {
  points: PathPoint[];
  color?: string;
  opacity?: number;
  weight?: number;
}

const PathDisplay: React.FC<PathDisplayProps> = ({ 
  points, 
  color = '#4285F4', // Google蓝色
  opacity = 0.8, 
  weight = 4 
}) => {
  // 如果没有点，不渲染任何内容
  if (!points || points.length < 2) {
    return null;
  }

  // 将后端返回的点转换为Google Maps API需要的格式
  const path = points.map((point) => ({
    lat: point.latitude,
    lng: point.longitude,
  }));

  return (
    <Polyline
      path={path}
      options={{
        strokeColor: color,
        strokeOpacity: opacity,
        strokeWeight: weight,
        geodesic: true,
        clickable: false,
        zIndex: 1,
      }}
    />
  );
};

export default PathDisplay; 