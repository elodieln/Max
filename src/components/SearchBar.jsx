// src/components/SearchBar.jsx
import React from 'react';

const SearchBar = ({ onSearch }) => {
  const handleSearchChange = (e) => {
    const searchValue = e.target.value;
    onSearch(searchValue);
  };

  return (
    <div className="w-full relative">
      <input
        type="text"
        placeholder="Rechercher un cours..."
        onChange={handleSearchChange}
        className="w-full px-4 py-2 md:py-3 rounded-lg border border-gray-200 
                 focus:outline-none focus:ring-2 focus:ring-max-primary focus:border-transparent
                 text-sm md:text-base"
      />
      <span className="absolute right-3 top-1/2 transform -translate-y-1/2">
        <svg
          className="w-4 h-4 md:w-5 md:h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </span>
    </div>
  );
};

export default SearchBar;