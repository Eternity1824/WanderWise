import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Location, Route, SortDirection, MapSettings } from '../types';

interface LocationContextType {
  locations: Location[];
  setLocations: (locations: Location[]) => void;
  selectedLocations: Location[];
  setSelectedLocations: (locations: Location[]) => void;
  currentRoute: Route | null;
  setCurrentRoute: (route: Route | null) => void;
  sortDirection: SortDirection;
  setSortDirection: (direction: SortDirection) => void;
  mapSettings: MapSettings;
  setMapSettings: (settings: MapSettings) => void;
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

interface LocationProviderProps {
  children: ReactNode;
}

export const LocationProvider: React.FC<LocationProviderProps> = ({ children }) => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<Location[]>([]);
  const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(SortDirection.NORTH_TO_SOUTH);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mapSettings, setMapSettings] = useState<MapSettings>({
    zoom: 12,
    center: {
      lat: 37.7749, // Default to San Francisco
      lng: -122.4194,
    },
  });

  return (
    <LocationContext.Provider
      value={{
        locations,
        setLocations,
        selectedLocations,
        setSelectedLocations,
        currentRoute,
        setCurrentRoute,
        sortDirection,
        setSortDirection,
        mapSettings,
        setMapSettings,
        isLoading,
        setIsLoading,
        error,
        setError,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocationContext = (): LocationContextType => {
  const context = useContext(LocationContext);
  if (context === undefined) {
    throw new Error('useLocationContext must be used within a LocationProvider');
  }
  return context;
}; 