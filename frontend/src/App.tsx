import React from 'react';
import './App.css';
import MapContainer from './components/map/MapContainer';
import NavigationPanel from './components/map/NavigationPanel';
import SearchBar from './components/map/SearchBar';
import { LocationProvider } from './context/LocationContext';

function App() {
  return (
    <LocationProvider>
      <div className="app">
        <div className="sidebar">
          <h1 className="app-title">WanderWise</h1>
          <SearchBar />
          <NavigationPanel />
        </div>
        <div className="map-wrapper">
          <MapContainer />
        </div>
      </div>
    </LocationProvider>
  );
}

export default App;
