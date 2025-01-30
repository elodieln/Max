import React from 'react';

const FilterButtons = ({ currentNiveau, onNiveauChange }) => {
  return (
    <div className="flex space-x-4 mb-8">
      <button
        onClick={() => onNiveauChange('ING1')}
        className={`px-6 py-2 rounded-lg font-medium transition-colors ${
          currentNiveau === 'ING1'
            ? 'bg-max-primary text-white'
            : 'bg-white text-max-primary border border-max-primary hover:bg-max-primary hover:text-white'
        }`}
      >
        ING1
      </button>
      <button
        onClick={() => onNiveauChange('ING2')}
        className={`px-6 py-2 rounded-lg font-medium transition-colors ${
          currentNiveau === 'ING2'
            ? 'bg-max-primary text-white'
            : 'bg-white text-max-primary border border-max-primary hover:bg-max-primary hover:text-white'
        }`}
      >
        ING2
      </button>
    </div>
  );
};

export default FilterButtons;