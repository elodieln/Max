import React from 'react';

const FilterButtons = ({ currentNiveau, onNiveauChange }) => {
  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => onNiveauChange('ING1')}
        className={`px-4 py-2 rounded-lg text-sm md:text-base font-medium transition-colors
          ${currentNiveau === 'ING1'
            ? 'bg-white text-max-primary'
            : 'bg-transparent text-white border border-white hover:bg-white hover:text-max-primary'
          }`}
      >
        ING1
      </button>
      <button
        onClick={() => onNiveauChange('ING2')}
        className={`px-4 py-2 rounded-lg text-sm md:text-base font-medium transition-colors
          ${currentNiveau === 'ING2'
            ? 'bg-white text-max-primary'
            : 'bg-transparent text-white border border-white hover:bg-white hover:text-max-primary'
          }`}
      >
        ING2
      </button>
    </div>
  );
};

export default FilterButtons;