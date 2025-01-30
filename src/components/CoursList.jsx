// src/components/CoursList.jsx
import React from 'react';
import CoursCard from './CoursCard';

const CoursList = ({ cours }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {cours.length === 0 ? (
        <div className="col-span-3 text-center py-8">
          <p className="text-white text-lg">Aucun cours disponible</p>
        </div>
      ) : (
        cours.map((cours) => (
          <CoursCard key={cours.id} cours={cours} />
        ))
      )}
    </div>
  );
};

export default CoursList;