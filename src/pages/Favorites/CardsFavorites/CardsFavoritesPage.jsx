import React, { useState, useEffect } from 'react';
import './CardsFavoritesPage.css';
import { getFavoriteFiles, removeFromFavorites } from '../../../services/filesService';

const CardsFavoritesPage = () => {
  const [favoriteFiles, setFavoriteFiles] = useState([]);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Charger les fichiers favoris depuis Supabase
  useEffect(() => {
    const loadFavorites = async () => {
      try {
        setLoading(true);
        const files = await getFavoriteFiles();
        setFavoriteFiles(files);
        
        // Sélectionner automatiquement le premier favori s'il existe
        if (files.length > 0) {
          setSelectedFileId(files[0].id);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des favoris:', error);
        setError("Impossible de charger vos fiches favorites");
      } finally {
        setLoading(false);
      }
    };
    
    loadFavorites();
  }, []);
  
  // Obtenir le fichier actuellement sélectionné
  const selectedFile = favoriteFiles.find(file => file.id === selectedFileId);

  // Fonction pour retirer un fichier des favoris
  const handleRemoveFromFavorites = async (fileId) => {
    try {
      await removeFromFavorites(fileId);
      
      // Mettre à jour la liste des favoris
      setFavoriteFiles(prev => prev.filter(file => file.id !== fileId));
      
      // Si le fichier actuellement sélectionné est retiré, sélectionner le premier favori restant
      if (fileId === selectedFileId) {
        const remainingFiles = favoriteFiles.filter(file => file.id !== fileId);
        setSelectedFileId(remainingFiles.length > 0 ? remainingFiles[0].id : null);
      }
    } catch (error) {
      console.error('Erreur lors du retrait des favoris:', error);
      setError(`Erreur: ${error.message}`);
    }
  };

  return (
    <div className="favorites-page-wrapper">
      <h1 className="favorites-page-title">Fiches et Quizz</h1>
      
      {loading ? (
        <div className="favorites-loading">
          <p>Chargement de vos fiches favorites...</p>
        </div>
      ) : error ? (
        <div className="favorites-error">
          <p>{error}</p>
        </div>
      ) : favoriteFiles.length === 0 ? (
        <div className="no-favorites-message">
          <p>Vous n'avez pas encore ajouté de fiches à vos favoris.</p>
          <p>Pour ajouter une fiche aux favoris, cliquez sur l'étoile à côté d'une fiche générée.</p>
        </div>
      ) : (
        <div className="favorites-content">
          <div className="favorites-sidebar">
            <h2 className="sidebar-title">Mes fiches favorites</h2>
            <div className="favorites-list">
              {favoriteFiles.map(file => (
                <div 
                  key={file.id} 
                  className={`favorite-item ${selectedFileId === file.id ? 'selected' : ''}`}
                  onClick={() => setSelectedFileId(file.id)}
                >
                  <div className="favorite-info">
                    <h3 className="favorite-title">{file.name}</h3>
                    <p className="favorite-date">
                      Généré le {new Date(file.created_at).toLocaleDateString('fr-FR', { 
                        year: 'numeric', 
                        month: '2-digit', 
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <button 
                    className="remove-favorite"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveFromFavorites(file.id);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FFD700" width="24" height="24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div className="favorites-main">
            {selectedFile ? (
              <div className="selected-file-viewer">
                <div className="file-header">
                  <h2 className="file-title">{selectedFile.name}</h2>
                  <div className="file-actions">
                    <a 
                      href={selectedFile.pdf_url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="action-button view-button"
                    >
                      Ouvrir dans un nouvel onglet
                    </a>
                    <a 
                      href={selectedFile.pdf_url} 
                      download={`Fiche_${selectedFile.name.replace(/\s+/g, '_')}.pdf`}
                      className="action-button download-button"
                    >
                      Télécharger
                    </a>
                  </div>
                </div>
                <div className="pdf-container">
                  <iframe
                    src={selectedFile.pdf_url}
                    title={selectedFile.name}
                    className="pdf-iframe"
                    frameBorder="0"
                  />
                </div>
              </div>
            ) : (
              <div className="empty-selection">
                <p>Sélectionnez une fiche dans la liste pour la visualiser</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CardsFavoritesPage;