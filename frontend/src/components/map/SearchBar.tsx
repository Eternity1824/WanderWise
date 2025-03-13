import React, { useState } from 'react';
import { useLocations } from '../../hooks/useLocations';

const SearchBar: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { searchLocations } = useLocations();

  // Handle search form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    searchLocations(searchQuery);
  };

  // Handle search input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  // Clear search
  const handleClear = () => {
    setSearchQuery('');
    searchLocations('');
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={searchQuery}
          onChange={handleChange}
          placeholder="搜索地点..."
          className="search-input"
        />
        <button type="submit" className="search-button">
          搜索
        </button>
        {searchQuery && (
          <button
            type="button"
            onClick={handleClear}
            className="clear-search-button"
          >
            清除
          </button>
        )}
      </form>
    </div>
  );
};

export default SearchBar; 