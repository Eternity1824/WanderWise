import React, { useState } from 'react';
import { useLocationContext } from '../context/LocationContext';
import { useLocations } from '../hooks/useLocations';

const SearchPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { searchLocations } = useLocations();
  const { isLoading } = useLocationContext();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchLocations(searchQuery);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="search-page">
      <h2>Could you please inform me of your plan?</h2>
      
      <div className="search-input-container">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={searchQuery}
            onChange={handleChange}
            placeholder="Enter your destination..."
            className="search-input"
          />
          
          <button 
            type="submit" 
            className="search-button"
            disabled={isLoading || !searchQuery.trim()}
          >
            {isLoading ? 'Searching...' : 'go'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchPage; 