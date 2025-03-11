import React, { useState, useEffect } from 'react';
import './CardsFavoritesPage.css';
// Correction du chemin d'importation - utiliser le chemin correct vers filesService
import { getFavoriteFiles, removeFromFavorites } from '../../../services/filesService';
import { supabase } from '../../../lib/supabase';

const CardsFavoritesPage = () => {
  const [favoriteFiles, setFavoriteFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Charger les favoris depuis Supabase au lieu du localStorage
    fetchFavoriteFiles();
  }, []);

  const fetchFavoriteFiles = async () => {
    try {
      setLoading(true);
      // Utiliser la fonction de votre service qui récupère les favoris depuis Supabase
      const files = await getFavoriteFiles();
      
      if (files && files.length > 0) {
        setFavoriteFiles(files);
        // Sélectionner automatiquement le premier favori
        setSelectedFileId(files[0].id);
      } else {
        setFavoriteFiles([]);
        setSelectedFileId(null);
      }
    } catch (err) {
      console.error("Erreur lors de la récupération des favoris:", err);
      setError("Impossible de charger vos fiches favorites");
    } finally {
      setLoading(false);
    }
  };

  // Obtenir le fichier actuellement sélectionné
  const selectedFile = favoriteFiles.find(file => file.id === selectedFileId);

  // Fonction pour retirer un fichier des favoris via Supabase
  const handleRemoveFromFavorites = async (fileId) => {
    try {
      // Appeler la fonction de votre service qui supprime les favoris de Supabase
      await removeFromFavorites(fileId);
      
      // Mettre à jour l'état local après la suppression
      const updatedFavorites = favoriteFiles.filter(file => file.id !== fileId);
      setFavoriteFiles(updatedFavorites);
      
      // Si le fichier actuellement sélectionné est retiré, sélectionner le premier favori restant
      if (fileId === selectedFileId) {
        setSelectedFileId(updatedFavorites.length > 0 ? updatedFavorites[0].id : null);
      }
    } catch (err) {
      console.error("Erreur lors de la suppression du favori:", err);
      setError("Impossible de retirer cette fiche des favoris");
    }
  };

  // Fonction pour télécharger un fichier
  const handleDownload = (file) => {
    if (!file || !file.pdf_url) {
      console.error("URL de téléchargement manquante");
      setError("Impossible de télécharger cette fiche: URL manquante");
      return;
    }

    try {
      // Créer un lien avec l'URL du PDF
      const link = document.createElement('a');
      link.href = file.pdf_url;
      
      // Définir un nom de fichier basé sur le nom de la fiche
      const fileName = `Fiche_${file.name.replace(/\s+/g, '_')}.pdf`;
      link.setAttribute('download', fileName);
      
      // Ajouter le lien au document, cliquer dessus, puis le supprimer
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Erreur lors du téléchargement:", error);
      setError("Erreur lors du téléchargement de la fiche");
    }
  };

  return (
    <div className="favorites-page-wrapper">
      <h1 className="favorites-page-title">Mes fiches favorites</h1>
      
      {loading ? (
        <div className="loading-message">
          <p>Chargement de vos favoris...</p>
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
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
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
                    <button 
                      onClick={() => handleDownload(selectedFile)}
                      className="action-button download-button"
                    >
                      Télécharger
                    </button>
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
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  );
};

export default CardsFavoritesPage;