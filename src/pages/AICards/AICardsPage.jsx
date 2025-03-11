import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AICardsPage.css';
import { saveGeneratedFile, addToFavorites, removeFromFavorites, isFileInFavorites } from '../../services/filesService';
import { supabase } from '../../lib/supabase';

const AICardsPage = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [savingToDb, setSavingToDb] = useState(false);
  const [generatedFile, setGeneratedFile] = useState(null);
  const [isFavorite, setIsFavorite] = useState(false);
  const [error, setError] = useState(null);
  
  // État pour l'historique des fiches
  const [recentFiles, setRecentFiles] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  // Nouvel état pour suivre les fiches favorites dans l'historique
  const [filesFavorites, setFilesFavorites] = useState({});

  // Charger l'historique des fiches au chargement du composant
  useEffect(() => {
    fetchRecentFiles();
  }, []);

  // Fonction pour récupérer les fiches récentes
  const fetchRecentFiles = async () => {
    try {
      setLoadingHistory(true);
      
      // Récupérer toutes les fiches
      const { data, error } = await supabase
        .from('cards')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10);

      if (error) {
        throw error;
      }

      setRecentFiles(data || []);
      
      // Vérifier pour chaque fiche si elle est en favoris
      const favorites = {};
      if (data && data.length > 0) {
        await Promise.all(data.map(async (file) => {
          const isFav = await isFileInFavorites(file.id);
          favorites[file.id] = isFav;
        }));
      }
      
      setFilesFavorites(favorites);
      
    } catch (err) {
      console.error("Erreur lors de la récupération des fichiers récents:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleGeneratePDF = async () => {
    if (!question.trim()) {
      setError("Veuillez saisir une question");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      console.log('Génération du PDF pour:', question);
      
      // Appel à l'API pour générer le PDF
      const response = await axios.post(
        'http://localhost:5000/generate-pdf',
        { question },
        { responseType: 'blob' }
      );

      // Créer une URL pour le blob
      const pdfBlob = new Blob([response.data], { type: 'application/pdf' });
      const pdfUrl = URL.createObjectURL(pdfBlob);
      
      // Générer un nom de fichier temporaire pour l'affichage
      const timestamp = new Date().getTime();
      const fileName = `Fiche_${question.substring(0, 20).replace(/\s+/g, '_')}_${timestamp}.pdf`;
      
      // Télécharger automatiquement le PDF
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Préparer les données du fichier
      const fileData = {
        name: question,
        fileName: fileName,
        url: pdfUrl,
        date: new Date().toLocaleString('fr-FR')
      };
      
      // Définir le fichier généré pour l'affichage immédiat
      setGeneratedFile(fileData);
      
      // Sauvegarder dans Supabase
      setSavingToDb(true);
      try {
        console.log("Tentative de sauvegarde dans Supabase");
        const fileId = await saveGeneratedFile(fileData, pdfBlob);
        console.log('Fichier sauvegardé avec ID:', fileId);
        
        // Mettre à jour l'objet du fichier généré avec l'ID
        setGeneratedFile(prev => ({
          ...prev,
          id: fileId
        }));
        
        // Vérifier si la fiche est déjà dans les favoris
        const fileIsFavorite = await isFileInFavorites(fileId);
        setIsFavorite(fileIsFavorite);
        
        // Rafraîchir la liste des fichiers récents
        fetchRecentFiles();
        
      } catch (dbError) {
        console.error('Erreur lors de la sauvegarde dans Supabase:', dbError);
        setError("Le PDF a été généré mais n'a pas pu être sauvegardé dans la base de données");
      } finally {
        setSavingToDb(false);
      }
      
      // Réinitialiser le champ de question
      setQuestion('');
      
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
      setError(`Erreur lors de la génération du PDF: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async () => {
    if (!generatedFile || !generatedFile.id) return;
    
    try {
      if (isFavorite) {
        await removeFromFavorites(generatedFile.id);
        setIsFavorite(false);
      } else {
        await addToFavorites(generatedFile.id);
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Erreur lors de la modification des favoris:', error);
      setError(`Erreur: ${error.message}`);
    }
  };

  // Nouvelle fonction pour basculer l'état de favori d'une fiche dans l'historique
  const toggleHistoryItemFavorite = async (fileId, event) => {
    // Empêcher l'événement de se propager (pour éviter d'ouvrir le fichier)
    event.stopPropagation();
    
    try {
      // Vérifier l'état actuel
      const currentIsFavorite = filesFavorites[fileId] || false;
      
      // Mettre à jour l'UI de manière optimiste
      setFilesFavorites(prev => ({
        ...prev,
        [fileId]: !currentIsFavorite
      }));
      
      // Mettre à jour la base de données
      if (currentIsFavorite) {
        await removeFromFavorites(fileId);
      } else {
        await addToFavorites(fileId);
      }
    } catch (error) {
      console.error('Erreur lors de la modification des favoris:', error);
      // Revenir à l'état précédent en cas d'erreur
      fetchRecentFiles();
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-32 md:pt-36 lg:pt-40"> 
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            Générer une fiche
          </h1>
        
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <div className="chatbot mb-8">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Sur quel sujet veux-tu faire une fiche ?"
              className="w-full p-3 rounded-lg mb-4 text-gray-800"
              disabled={loading || savingToDb}
            />
            <button 
              onClick={handleGeneratePDF} 
              disabled={loading || savingToDb || !question.trim()}
              className={`px-6 py-3 rounded-lg bg-[#FF914D] text-white font-bold ${loading || savingToDb || !question.trim() ? 'opacity-70 cursor-not-allowed' : 'hover:bg-[#F9BC97]'}`}
            >
              {loading ? 'Génération en cours...' : savingToDb ? 'Sauvegarde en cours...' : 'Générer'}
            </button>
          </div>
          
          {/* Affichage de la fiche générée */}
          {generatedFile && (
            <div className="bg-white rounded-lg p-6 shadow-lg mb-8">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold mb-2 text-gray-800">Fiche générée</h2>
                  <h3 className="font-bold text-lg mb-1">{generatedFile.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">Généré le {generatedFile.date}</p>
                </div>
                <button 
                  onClick={toggleFavorite}
                  disabled={!generatedFile.id || savingToDb}
                  className={`focus:outline-none ${!generatedFile.id || savingToDb ? 'opacity-50 cursor-not-allowed' : ''}`}
                  aria-label={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
                >
                  {isFavorite ? (
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FFD700" width="24" height="24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#808080" width="24" height="24">
                      <path d="M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z" />
                    </svg>
                  )}
                </button>
              </div>
              <div className="mt-4">
                <iframe
                  src={generatedFile.url}
                  title={generatedFile.name}
                  className="w-full h-96 border rounded-lg"
                  frameBorder="0"
                />
              </div>
              <div className="mt-4 flex space-x-3">
                <a 
                  href={generatedFile.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="px-4 py-2 bg-[#007179] text-white rounded-lg hover:opacity-90"
                >
                  Ouvrir dans un nouvel onglet
                </a>
                <a 
                  href={generatedFile.url} 
                  download={generatedFile.fileName}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
                >
                  Télécharger à nouveau
                </a>
              </div>
            </div>
          )}
          
          {/* Historique des fiches */}
          <div className="mt-8">
            <h2 className="text-xl font-bold text-white mb-4">Historique des fiches</h2>
            {loadingHistory ? (
              <div className="bg-white rounded-lg p-4 text-center">
                Chargement de l'historique...
              </div>
            ) : recentFiles.length === 0 ? (
              <div className="bg-white rounded-lg p-4 text-center">
                Aucune fiche dans l'historique
              </div>
            ) : (
              <div className="bg-white rounded-lg p-4">
                {recentFiles.map(file => (
                  <div 
                    key={file.id} 
                    className="border-b last:border-b-0 py-3 px-2 hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => window.open(file.pdf_url, '_blank')}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-semibold text-gray-800">{file.name}</h3>
                        <p className="text-sm text-gray-600">
                          {new Date(file.created_at).toLocaleDateString('fr-FR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      <div className="flex space-x-2 items-center">
                        {/* Ajout de l'étoile de favori */}
                        <button 
                          onClick={(e) => toggleHistoryItemFavorite(file.id, e)}
                          className="focus:outline-none"
                          aria-label={filesFavorites[file.id] ? "Retirer des favoris" : "Ajouter aux favoris"}
                        >
                          {filesFavorites[file.id] ? (
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FFD700" width="20" height="20">
                              <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#808080" width="20" height="20">
                              <path d="M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z" />
                            </svg>
                          )}
                        </button>
                        
                        <a 
                          href={file.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm px-3 py-1 bg-[#007179] text-white rounded-lg hover:opacity-90"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Voir
                        </a>
                        
                        <a 
                          href={file.pdf_url}
                          download={`Fiche_${file.name.replace(/\s+/g, '_')}.pdf`}
                          className="text-sm px-3 py-1 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Télécharger
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICardsPage;