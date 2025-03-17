import React, { useState, useEffect, useRef } from 'react';
import { askQuestion } from '../../services/api/chatbot';
import './ChatbotPage.css';

const ChatbotPage = () => {
  // État pour stocker les messages
  const [messages, setMessages] = useState([
    // Message de bienvenue initial
    {
      id: 1,
      text: "Bonjour, je suis Max, votre assistant pour l'électronique! Comment puis-je vous aider aujourd'hui?",
      sender: 'bot'
    }
  ]);
  
  // État pour le message en cours de saisie
  const [inputMessage, setInputMessage] = useState('');
  
  // État pour indiquer qu'une réponse est en cours de chargement
  const [isLoading, setIsLoading] = useState(false);
  
  // Référence pour faire défiler automatiquement vers le dernier message
  const messagesEndRef = useRef(null);

  // Effet pour faire défiler vers le dernier message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Fonction pour gérer l'envoi d'un message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;
    
    // Ajouter le message de l'utilisateur à la liste des messages
    const newUserMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user'
    };
    
    setMessages([...messages, newUserMessage]);
    
    // Sauvegarder et vider l'entrée utilisateur
    const question = inputMessage;
    setInputMessage('');
    
    // Indiquer le chargement
    setIsLoading(true);
    
    try {
      // Appel API pour obtenir la réponse
      const response = await askQuestion(question);
      
      // Ajouter la réponse du bot
      const botResponse = {
        id: Date.now() + 1,
        text: response.response || "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.",
        sender: 'bot',
        // Ajout de métadonnées du modèle si disponibles
        metadata: {
          model: response.model_used,
          processingTime: response.processing_time
        }
      };
      
      setMessages(prevMessages => [...prevMessages, botResponse]);
    } catch (error) {
      // En cas d'erreur, ajouter un message d'erreur
      const errorMessage = {
        id: Date.now() + 1,
        text: "Une erreur est survenue lors de la communication avec le serveur. Veuillez réessayer plus tard.",
        sender: 'bot',
        error: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      // Fin du chargement
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-32 md:pt-36 lg:pt-40">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            Max, le chatbot
          </h1>
          
          <div className="chatbot-container">
            {/* Zone d'affichage des messages */}
            <div className="messages-container">
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}
                             ${message.error ? 'error-message' : ''}`}
                >
                  {message.text}
                  {message.metadata && (
                    <div className="message-metadata">
                      <small>Modèle: {message.metadata.model} | Temps: {message.metadata.processingTime?.toFixed(2)}s</small>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Indicateur de chargement */}
              {isLoading && (
                <div className="message bot-message loading-message">
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
              
              {/* Élément pour le défilement automatique */}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Formulaire de saisie */}
            <form onSubmit={handleSendMessage} className="message-form">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Posez votre question sur l'électronique..."
                className="message-input"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className={`send-button ${isLoading ? 'disabled' : ''}`}
                disabled={isLoading}
              >
                {isLoading ? 'Envoi...' : 'Envoyer'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;