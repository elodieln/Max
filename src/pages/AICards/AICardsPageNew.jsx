// Mettre à jour src/pages/AICards/AICardsPageNew.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FiFileText, FiX, FiDownload, FiAlertCircle, FiCheckCircle, FiEye } from 'react-icons/fi';
import CardViewer from '../../components/CardViewer/CardViewer';
import './AICardsPageNew.css';

const exampleTopics = [
  "Transistors bipolaires",
  "Filtres actifs",
  "Amplificateurs opérationnels",
  "Convertisseurs A/N",
  "Théorème de Thévenin",
  "Transformateurs",
  "Diodes Zener"
];

const AICardsPage = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const [cardData, setCardData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    setCharCount(question.length);
  }, [question]);

  const handleGenerateCard = async (shouldDownload = false) => {
    if (!question.trim()) {
      setError("Veuillez entrer un sujet pour générer une fiche.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      console.log('Génération de fiche sur:', question);
      
      // Récupérer d'abord les données JSON
      const dataResponse = await axios.post(
        'http://localhost:5001/generate-card-data',
        { question }
      );
      
      // Si la requête a réussi et contient des données
      if (dataResponse.data.success && dataResponse.data.data) {
        setCardData(dataResponse.data.data);
        setShowPreview(true);
        
        // Si l'utilisateur a cliqué sur "Télécharger la fiche", générer le PDF
        if (shouldDownload) {
          await handleDownloadPDF();
        }
        
        setSuccess(true);
        setTimeout(() => setSuccess(false), 5000);
      }

    } catch (error) {
      console.error('Erreur lors de la génération de la fiche:', error);
      setError("Une erreur est survenue lors de la génération de la fiche. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:5001/generate-pdf',
        { question },
        { responseType: 'blob' }
      );

      // Créer une URL temporaire
      const pdfBlob = new Blob([response.data], { type: 'application/pdf' });
      const pdfUrl = window.URL.createObjectURL(pdfBlob);

      // Créer un lien <a> et déclencher un clic pour télécharger automatiquement
      const link = document.createElement('a');
      link.href = pdfUrl;
      
      // Formater le nom du fichier pour qu'il soit plus descriptif
      const fileName = `Fiche_${question.slice(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}`;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Libérer l'URL temporaire
      window.URL.revokeObjectURL(pdfUrl);
      
    } catch (error) {
      console.error('Erreur lors du téléchargement du PDF:', error);
      setError("Une erreur est survenue lors du téléchargement de la fiche.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearInput = () => {
    setQuestion('');
    setError(null);
    setSuccess(false);
  };

  const handleExampleClick = (example) => {
    setQuestion(example);
    setError(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-32 md:pt-36 lg:pt-40">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            Générateur de fiches
          </h1>

          <div className="card-generator">
            <div className="card-generator-header">
              <h2>Créer une fiche de cours</h2>
              <p>
                Obtenez une fiche complète avec explications, concepts clés et exercices sur n'importe quel sujet d'électronique.
              </p>
            </div>

            <div className="card-generator-body">
              {error && (
                <div className="error-message">
                  <FiAlertCircle />
                  <span>{error}</span>
                </div>
              )}

              {success && (
                <div className="success-message">
                  <FiCheckCircle />
                  <span>Votre fiche a été générée avec succès !</span>
                </div>
              )}

              <div className="card-generator-input">
                <label htmlFor="topic">Sujet de la fiche</label>
                <textarea
                  id="topic"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Décrivez précisément le sujet pour lequel vous souhaitez générer une fiche (ex: les condensateurs, les convertisseurs analogiques-numériques, etc.)"
                  disabled={loading}
                  maxLength={500}
                />
                <div className="flex justify-end mt-1 text-sm text-gray-500">
                  {charCount}/500 caractères
                </div>
              </div>

              <div className="card-generator-buttons">
                <button 
                  className="generate-button"
                  onClick={() => handleGenerateCard(true)} 
                  disabled={loading || !question.trim()}
                >
                  {loading ? (
                    <>
                      <div className="loader"></div>
                      <span>Génération...</span>
                    </>
                  ) : (
                    <>
                      <FiDownload />
                      <span>Télécharger la fiche</span>
                    </>
                  )}
                </button>

                <button 
                  className="generate-button"
                  onClick={() => handleGenerateCard(false)}
                  disabled={loading || !question.trim()}
                  style={{ backgroundColor: '#0D8A94' }}
                >
                  <FiEye />
                  <span>Prévisualiser</span>
                </button>

                <button 
                  className="clear-button"
                  onClick={handleClearInput}
                  disabled={loading || !question.trim()}
                >
                  <FiX />
                  <span>Effacer</span>
                </button>
              </div>

              <div className="example-suggestions">
                <h3>Suggestions de sujets</h3>
                <div className="example-tags">
                  {exampleTopics.map((topic, index) => (
                    <button
                      key={index}
                      className="example-tag"
                      onClick={() => handleExampleClick(topic)}
                      disabled={loading}
                    >
                      {topic}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Prévisualisation de la fiche */}
          {showPreview && cardData && (
            <CardViewer 
              cardData={cardData} 
              onDownload={handleDownloadPDF} 
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AICardsPage;