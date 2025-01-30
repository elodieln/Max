import React from 'react';
import CoursCard from './CoursCard';

const CoursList = ({ cours }) => {
  return cours.length === 0 ? (
    <div className="flex justify-center py-8">
      <p className="text-white text-lg">Aucun cours disponible</p>
    </div>
  ) : (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
      {cours.map((cours) => (
        <CoursCard key={cours.id} cours={cours} />
      ))}
    </div>
  );
};

export default CoursList;