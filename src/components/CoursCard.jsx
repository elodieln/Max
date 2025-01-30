import React from 'react';
import { AiFillStar } from 'react-icons/ai';

const CoursCard = ({ cours, onFavoriToggle }) => {
  const { id, fields } = cours;
  const isFavori = fields.favori || false;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative">
        <img
          src={fields.photo || '/placeholder-image.jpg'}
          alt={fields.Nom_Cours}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-4 right-4">
          <button onClick={() => onFavoriToggle(id, !isFavori)} className="p-2 rounded-full bg-white shadow-md hover:bg-gray-100 transition-colors">
            <AiFillStar
              className={`h-6 w-6 ${isFavori ? 'text-yellow-400' : 'text-gray-400'}`}
            />
          </button>
        </div>
        <div className="absolute top-4 left-4">
          <span className="bg-white px-3 py-1 rounded-full text-sm font-medium text-max-primary">
            {fields.Année}
          </span>
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-bold text-xl mb-2 text-gray-900">{fields.Nom_Cours}</h3>
        <div className="mt-4">
          <div
            className="inline-block w-full text-center bg-max-primary text-white py-2 px-4 rounded-lg hover:bg-max-primary/90 transition-colors"
            onClick={() => window.open(fields.Cours, '_blank', 'noopener,noreferrer')}
          >
            Voir le cours
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoursCard;