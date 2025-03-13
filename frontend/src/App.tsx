import React, { useState } from 'react';
import './App.css';
import MapContainer from './components/map/MapContainer';
import NavigationPanel from './components/map/NavigationPanel';
import SearchBar from './components/map/SearchBar';
import { LocationProvider } from './context/LocationContext';
import SearchPage from './components/SearchPage';

function App() {
  const [activeButton, setActiveButton] = useState<number | null>(null);

  const toggleButton = (buttonNumber: number) => {
    if (activeButton === buttonNumber) {
      setActiveButton(null);
    } else {
      setActiveButton(buttonNumber);
    }
  };

  return (
    <LocationProvider>
      <div className="app">
        {/* Left Navigation Bar */}
        <div className="nav-bar">
          <div className="nav-logo">W</div>
          <button 
            className={`nav-button ${activeButton === 1 ? 'active' : ''}`}
            onClick={() => toggleButton(1)}
          >
            1
          </button>
          <button 
            className={`nav-button ${activeButton === 2 ? 'active' : ''}`}
            onClick={() => toggleButton(2)}
          >
            2
          </button>
          <button 
            className={`nav-button ${activeButton === 3 ? 'active' : ''}`}
            onClick={() => toggleButton(3)}
          >
            3
          </button>
        </div>

        {/* Search Page (shown when button 1 is active) */}
        {activeButton === 1 && <SearchPage />}

        {/* Original sidebar (hidden) */}
        <div className="sidebar">
          <h1 className="app-title">WanderWise</h1>
          <SearchBar />
          <NavigationPanel />
        </div>

        {/* Map Container */}
        <div className="map-wrapper">
          <MapContainer />
        </div>
      </div>
    </LocationProvider>
  );
}

export default App;
