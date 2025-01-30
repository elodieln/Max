import React from 'react';
import CoursCard from './CoursCard';

const CoursList = ({ cours, onFavoriToggle }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cours.map((cours) => (
        <CoursCard 
          key={cours.id} 
          cours={cours} 
          onFavoriToggle={onFavoriToggle}
        />
      ))}
    </div>
  );
};

export default CoursList;