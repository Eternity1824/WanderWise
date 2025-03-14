import React, { createContext, useContext, useState, ReactNode, Dispatch, SetStateAction } from 'react';
import { Location, Route, SortDirection, MapSettings, PathPoint } from '../types';

interface LocationContextType {
  locations: Location[];
  setLocations: Dispatch<SetStateAction<Location[]>>;
  selectedLocations: Location[];
  setSelectedLocations: Dispatch<SetStateAction<Location[]>>;
  currentRoute: Route | null;
  setCurrentRoute: Dispatch<SetStateAction<Route | null>>;
  pathPoints: PathPoint[];
  setPathPoints: Dispatch<SetStateAction<PathPoint[]>>;
  sortDirection: SortDirection;
  setSortDirection: Dispatch<SetStateAction<SortDirection>>;
  mapSettings: MapSettings;
  setMapSettings: Dispatch<SetStateAction<MapSettings>>;
  isLoading: boolean;
  setIsLoading: Dispatch<SetStateAction<boolean>>;
  error: string | null;
  setError: Dispatch<SetStateAction<string | null>>;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

interface LocationProviderProps {
  children: ReactNode;
}

export const LocationProvider: React.FC<LocationProviderProps> = ({ children }) => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<Location[]>([]);
  const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
  const [pathPoints, setPathPoints] = useState<PathPoint[]>([]);
  const [sortDirection, setSortDirection] = useState<SortDirection>(SortDirection.NORTH_TO_SOUTH);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mapSettings, setMapSettings] = useState<MapSettings>({
    zoom: 13,
    center: {
      lat: 47.6062, // Default to Seattle
      lng: -122.3321,
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
        pathPoints,
        setPathPoints,
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