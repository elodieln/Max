import React, { useState, useEffect } from 'react';
import './SavedCards.css';

const SavedCards = () => {
  const [favorites, setFavorites] = useState([]);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    // Charger les données sauvegardées en localStorage
    const savedFiles = localStorage.getItem('maxGeneratedFiles');
    const savedFavorites = localStorage.getItem('maxFavoriteFiles');
    
    if (savedFiles) setGeneratedFiles(JSON.parse(savedFiles));
    if (savedFavorites) setFavorites(JSON.parse(savedFavorites));
    setLoading(false);
  }, []);

  // Filtrer les fichiers favoris
  const favoriteFiles = generatedFiles.filter(file => favorites.includes(file.id));

  // Fonction pour retirer un fichier des favoris
  const removeFromFavorites = (fileId) => {
    const updatedFavorites = favorites.filter(id => id !== fileId);
    setFavorites(updatedFavorites);
    localStorage.setItem('maxFavoriteFiles', JSON.stringify(updatedFavorites));
    
    // Si le fichier actuellement sélectionné est retiré des favoris, désélectionner
    if (selectedFile && selectedFile.id === fileId) {
      setSelectedFile(null);
    }
  };

  // Fonction pour sélectionner une fiche à afficher
  const selectFile = (file) => {
    setSelectedFile(file);
  };

  if (loading) {
    return <div className="max-loading">Chargement des favoris...</div>;
  }

  return (
    <div className="max-favorites-container">
      {favoriteFiles.length === 0 ? (
        <div className="max-no-favorites">
          <p>Vous n'avez pas encore ajouté de fiches à vos favoris.</p>
          <p>Pour ajouter une fiche aux favoris, cliquez sur l'étoile à côté d'une fiche générée.</p>
        </div>
      ) : (
        <div className="max-favorites-layout">
          {/* Liste des fiches favorites à gauche */}
          <div className="max-favorites-list">
            <h2 className="max-favorites-title">Mes fiches favorites</h2>
            {favoriteFiles.map(file => (
              <div 
                key={file.id} 
                className={`max-favorite-card ${selectedFile && selectedFile.id === file.id ? 'max-favorite-selected' : ''}`}
                onClick={() => selectFile(file)}
              >
                <div className="max-favorite-card-header">
                  <h3 className="max-favorite-card-title">{file.name}</h3>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFromFavorites(file.id);
                    }}
                    className="max-remove-favorite"
                    aria-label="Retirer des favoris"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FFD700" width="20" height="20">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  </button>
                </div>
                <p className="max-favorite-card-date">Généré le {file.date}</p>
              </div>
            ))}
          </div>

          {/* Affichage de la fiche sélectionnée à droite */}
          <div className="max-favorites-viewer">
            {selectedFile ? (
              <div className="max-selected-file">
                <div className="max-selected-file-header">
                  <h2 className="max-selected-file-title">{selectedFile.name}</h2>
                  <div className="max-selected-file-actions">
                    <a 
                      href={selectedFile.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="max-view-button"
                    >
                      Ouvrir dans un nouvel onglet
                    </a>
                    <a 
                      href={selectedFile.url} 
                      download={selectedFile.fileName}
                      className="max-download-button"
                    >
                      Télécharger
                    </a>
                  </div>
                </div>
                <div className="max-selected-file-preview">
                  <iframe
                    src={selectedFile.url}
                    title={selectedFile.name}
                    className="max-pdf-iframe"
                    frameBorder="0"
                  />
                </div>
              </div>
            ) : (
              <div className="max-no-selection">
                <p>Sélectionnez une fiche à gauche pour la visualiser ici</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedCards;