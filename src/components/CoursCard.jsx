// src/components/CoursCard.jsx
import React, { useState, useEffect } from 'react';
import { AiFillStar } from 'react-icons/ai';
import { addToFavorites, removeFromFavorites, checkIsFavorite } from '../services/favorites';

const CoursCard = ({ cours }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const defaultImage = "https://placehold.co/600x400/007179/FFFFFF/png?text=Cours";

  useEffect(() => {
    const checkFavoriteStatus = async () => {
      try {
        const status = await checkIsFavorite(cours.id);
        setIsFavorite(status);
      } catch (error) {
        console.error('Erreur lors de la vérification du statut favori:', error);
      }
    };

    checkFavoriteStatus();
  }, [cours.id]);

  const handleFavoriteClick = async (e) => {
    e.stopPropagation();
    if (isLoading) return;

    setIsLoading(true);
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
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="h-full bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
      onClick={() => cours.pdf_url && window.open(cours.pdf_url, '_blank', 'noopener noreferrer')}
    >
      <div className="relative">
        <div className="absolute top-4 left-4 z-10">
          <span className="bg-white px-3 py-1 rounded-full text-sm font-medium text-max-primary">
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
            className={`p-2 rounded-full bg-white shadow-md hover:bg-gray-100 transition-colors 
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={handleFavoriteClick}
            disabled={isLoading}
            aria-label={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
          >
            <AiFillStar 
              className={`h-6 w-6 transition-colors ${
                isFavorite ? 'text-max-accent' : 'text-gray-400'
              }`} 
            />
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