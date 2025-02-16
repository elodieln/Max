
import React, { useState } from 'react';
import axios from 'axios';
import './AICardsPage.css';


const Chatbot = () => {
  const [question, setQuestion] = useState('');
  const [pdfUrl, setPdfUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGeneratePDF = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/generate-pdf', { question });
      setPdfUrl(response.data.pdfPath);
    } catch (error) {
      console.error('Erreur lors de la génération du PDF', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-32 md:pt-36 lg:pt-40"> 
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            Générer une fiche
          </h1>
        
          <div className="chatbot">
      
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Sur quel sujet veux-tu faire une fiche ?"
            />
            <button onClick={handleGeneratePDF} disabled={loading}>
              {loading ? 'Génération en cours...' : 'Générer'}
            </button>
            {pdfUrl && (
              <div>
                <p>PDF généré avec succès !</p>
                <a href={pdfUrl} target="_blank" rel="noopener noreferrer">Télécharger le PDF</a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    
  );
};

export default Chatbot;
