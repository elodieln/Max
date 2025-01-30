import React from 'react';
import CoursCard from './CoursCard';

const CoursList = ({ cours }) => {
  if (!cours || cours.length === 0) {
    return (
      <div className="text-center text-white py-8">
        Aucun cours disponible
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cours.map((cours) => (
        <CoursCard 
          key={cours.id} 
          cours={cours}
        />
      ))}
    </div>
  );
};

export default CoursList;