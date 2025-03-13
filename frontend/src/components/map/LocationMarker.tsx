import React, { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { Location } from '../../types';
import { useLocationContext } from '../../context/LocationContext';

interface LocationMarkerProps {
  location: Location;
  isSelected: boolean;
}

const LocationMarker: React.FC<LocationMarkerProps> = ({ location, isSelected }) => {
  const [isInfoOpen, setIsInfoOpen] = useState(false);
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
  };

  // Close info window
  const closeInfoWindow = () => {
    setIsInfoOpen(false);
  };

  return (
    <>
      <Marker
        position={location.position}
        onClick={toggleInfoWindow}
        onDblClick={toggleSelection}
        icon={{
          url: isSelected
            ? 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            : 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
          scaledSize: new window.google.maps.Size(40, 40),
        }}
        animation={window.google.maps.Animation.DROP}
        title={location.name}
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
            {location.category && <p><strong>类别:</strong> {location.category}</p>}
            {location.rating && (
              <p>
                <strong>评分:</strong> {location.rating} / 5
                <span className="stars">
                  {'★'.repeat(Math.floor(location.rating))}
                  {'☆'.repeat(5 - Math.floor(location.rating))}
                </span>
              </p>
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