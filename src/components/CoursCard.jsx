import React from 'react';
import { AiFillStar } from 'react-icons/ai';

const CoursCard = ({ cours }) => {
  const defaultImage = "https://placehold.co/600x400/007179/FFFFFF/png?text=Cours"; // Image par défaut

  return (
    <div className="h-full bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative">
        <img
          src={cours.photo_url || '/placeholder-course.jpg'}
          alt={cours.name}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-4 right-4">
          <button 
            className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100 transition-colors"
          >
            <AiFillStar className="h-6 w-6 text-gray-400" />
          </button>
        </div>
        <div className="absolute top-4 left-4">
          <span className="bg-white px-3 py-1 rounded-full text-sm font-medium text-max-primary">
            {cours.year}
          </span>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-bold text-xl mb-2 text-gray-900">{cours.name}</h3>
        <div className="mt-4">
          
            href={cours.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block w-full text-center bg-max-primary text-white py-2 px-4 rounded-lg hover:bg-max-primary/90 transition-colors"
          <a>
            Voir le cours
          </a>
        </div>
      </div>
    </div>
  );
};

export default CoursCard;