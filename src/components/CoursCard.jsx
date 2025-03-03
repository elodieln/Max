import React, { useState, useEffect } from 'react';
import { AiFillStar } from 'react-icons/ai';
import { addToFavorites, removeFromFavorites, checkIsFavorite } from '../services/favorites';

const CoursCard = ({ cours }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const defaultImage = "https://placehold.co/600x400/007179/FFFFFF/png?text=Cours";

  // Vérifier si le cours est dans les favoris au chargement
  useEffect(() => {
    const checkFavorite = async () => {
      const isCourseFavorite = await checkIsFavorite(cours.id);
      setIsFavorite(isCourseFavorite);
    };
    checkFavorite();
  }, [cours.id]);

  const handleCardClick = () => {
    if (cours.pdf_url) {
      window.open(cours.pdf_url, '_blank', 'noopener noreferrer');
    }
  };

  const handleFavoriteClick = async (e) => {
    e.stopPropagation();
    try {
      if (isFavorite) {
        await removeFromFavorites(cours.id);
        setIsFavorite(false);
      } else {
        await addToFavorites(cours.id);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Erreur lors de la gestion des favoris:', error);
    }
  };

  return (
    <div 
      className="h-full bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="relative">
        <div className="absolute top-4 left-4 z-10">
          <span className="bg-white px-3 py-1 rounded-full text-sm font-medium text-[#007179]">
            {cours.year}
          </span>
        </div>
        <img
          src={cours.photo_url || defaultImage}
          alt={cours.name}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-4 right-4 z-10">
          <button 
            className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100 transition-colors"
            onClick={handleFavoriteClick}
            aria-label={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
          >
            <AiFillStar className={`h-6 w-6 ${isFavorite ? 'text-yellow-400' : 'text-gray-400'}`} />
          </button>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-bold text-xl text-gray-900">{cours.name}</h3>
      </div>
    </div>
  );
};

export default CoursCard;