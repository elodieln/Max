// src/components/CoursCard.jsx
import React from 'react';
import { AiFillStar } from 'react-icons/ai';

const CoursCard = ({ cours }) => {

  const defaultImage = "https://placehold.co/600x400/007179/FFFFFF/png?text=Cours";

  const handleCardClick = () => {
    if (cours.pdf_url) {
      window.open(cours.pdf_url, '_blank', 'noopener noreferrer');
    }
  };

  return (
    <div 
      className="h-full bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="relative">
        {/* Badge ING2 */}
        <div className="absolute top-4 left-4 z-10">
          <span className="bg-white px-3 py-1 rounded-full text-sm font-medium text-max-primary">
            {cours.year}
          </span>
        </div>

        {/* Image */}
        <img
          src={cours.photo_url || defaultImage}
          alt={cours.name}
          className="w-full h-48 object-cover"
        />

        {/* Bouton favoris */}
        <div className="absolute top-4 right-4 z-10">
          <button 
            className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100 transition-colors"
            onClick={(e) => {
              e.stopPropagation(); // Empêche le déclenchement du clic de la carte
              // Logique pour ajouter aux favoris (à implémenter plus tard)
            }}
            aria-label="Ajouter aux favoris"
          >
            <AiFillStar className="h-6 w-6 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="p-4">
        {/* Titre du cours */}
        <h3 className="font-bold text-xl text-gray-900">{cours.name}</h3>
      </div>
    </div>
  );
};

export default CoursCard;