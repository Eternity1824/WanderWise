import { useState } from 'react';
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
            title="搜索"
          >
            {/* 放大镜图标 */}
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </button>
          <button 
            className={`nav-button ${activeButton === 2 ? 'active' : ''}`}
            onClick={() => toggleButton(2)}
            title="收藏"
          >
            {/* 五角星图标 */}
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
          </button>
          <button 
            className={`nav-button ${activeButton === 3 ? 'active' : ''}`}
            onClick={() => toggleButton(3)}
            title="设置"
          >
            {/* 齿轮图标 */}
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
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
