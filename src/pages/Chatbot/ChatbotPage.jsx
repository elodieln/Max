import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { TypeAnimation } from 'react-type-animation';
import { askQuestion } from '../../services/api/chatbot';
import { 
  createConversation, 
  saveMessage, 
  loadConversationHistory 
} from '../../services/chat/history';
import ChatHistory from '../../components/ChatHistory';
import './ChatbotPage.css';

const ChatbotPage = () => {
  // État pour stocker les messages
  const [messages, setMessages] = useState([]);
  
  // État pour le message en cours de saisie
  const [inputMessage, setInputMessage] = useState('');
  
  // État pour indiquer qu'une réponse est en cours de chargement
  const [isLoading, setIsLoading] = useState(false);
  
  // ID de la conversation en cours
  const [conversationId, setConversationId] = useState(null);
  
  // État pour contrôler l'animation de frappe
  const [isTyping, setIsTyping] = useState(false);
  const [currentTypingText, setCurrentTypingText] = useState('');
  
  // État pour contrôler l'affichage de l'historique sur mobile
  const [showHistory, setShowHistory] = useState(false);
  
  // Référence pour faire défiler automatiquement vers le dernier message
  const messagesEndRef = useRef(null);

  // Initialisation de la conversation
  useEffect(() => {
    initializeConversation(null);
  }, []);

  // Fonction pour initialiser une nouvelle conversation ou charger une existante
  const initializeConversation = async (existingConversationId) => {
    setMessages([]);
    setIsLoading(true);
    
    if (existingConversationId) {
      // Charger une conversation existante
      setConversationId(existingConversationId);
      try {
        const history = await loadConversationHistory(existingConversationId);
        setMessages(history);
      } catch (error) {
        console.error("Erreur lors du chargement de l'historique:", error);
      }
    } else {
      // Créer une nouvelle conversation
      const newConversationId = createConversation();
      setConversationId(newConversationId);
      
      // Message de bienvenue initial
      const welcomeMessage = {
        id: 1,
        text: "Bonjour, je suis Max, votre assistant pour l'électronique! Comment puis-je vous aider aujourd'hui?",
        sender: 'bot'
      };
      
      setMessages([welcomeMessage]);
      
      // Sauvegarder le message de bienvenue
      try {
        await saveMessage(welcomeMessage, newConversationId);
      } catch (error) {
        console.error("Erreur lors de la sauvegarde du message de bienvenue:", error);
      }
    }
    
    setIsLoading(false);
  };
  
  // Effet pour faire défiler vers le dernier message
  useEffect(() => {
    if (messagesEndRef.current) {
      // Utiliser un délai court pour permettre au rendu de se terminer
      const timer = setTimeout(() => {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages, isTyping]);
  
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
    
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    
    // Sauvegarder le message de l'utilisateur
    try {
      await saveMessage(newUserMessage, conversationId);
    } catch (error) {
      console.error("Erreur lors de la sauvegarde du message:", error);
    }
    
    // Sauvegarder et vider l'entrée utilisateur
    const question = inputMessage;
    setInputMessage('');
    
    // Indiquer le chargement avec un message de réflexion
    setIsLoading(true);
    
    // Ajouter un message temporaire "En réflexion" qui sera remplacé
    const thinkingMessage = {
      id: 'thinking',
      text: "Je réfléchis à votre question...",
      sender: 'bot',
      isThinking: true
    };
    
    setMessages(prevMessages => [...prevMessages, thinkingMessage]);
    
    try {
      // Appel API pour obtenir la réponse
      const response = await askQuestion(question);
      
      // Retirer le message "thinking"
      setMessages(prevMessages => prevMessages.filter(m => m.id !== 'thinking'));
      
      // Préparation de la réponse du bot
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
      
      // Activation de l'effet de frappe
      setIsTyping(true);
      setCurrentTypingText(botResponse.text);
      
      // Sauvegarder la réponse du bot
      try {
        await saveMessage(botResponse, conversationId);
      } catch (error) {
        console.error("Erreur lors de la sauvegarde de la réponse:", error);
      }
      
      // Ajouter la réponse complète après l'animation
      // Ajuster la vitesse pour que l'animation soit plus rapide
      const typingSpeed = Math.min(15, Math.max(5, botResponse.text.length / 100));
      
      setTimeout(() => {
        setIsTyping(false);
        setMessages(prevMessages => [...prevMessages, botResponse]);
      }, botResponse.text.length * typingSpeed);
      
    } catch (error) {
      // Retirer le message "thinking"
      setMessages(prevMessages => prevMessages.filter(m => m.id !== 'thinking'));
      
      // En cas d'erreur, ajouter un message d'erreur
      const errorMessage = {
        id: Date.now() + 1,
        text: "Une erreur est survenue lors de la communication avec le serveur. Veuillez réessayer plus tard.",
        sender: 'bot',
        error: true
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      
      // Sauvegarder le message d'erreur
      try {
        await saveMessage(errorMessage, conversationId);
      } catch (saveError) {
        console.error("Erreur lors de la sauvegarde du message d'erreur:", saveError);
      }
      
    } finally {
      // Fin du chargement (seulement si nous ne sommes pas en train de taper)
      if (!isTyping) {
        setIsLoading(false);
      } else {
        // Si l'effet de frappe est en cours, attendre qu'il se termine avant de réinitialiser isLoading
        const typingSpeed = Math.min(15, Math.max(5, currentTypingText.length / 100));
        setTimeout(() => {
          setIsLoading(false);
        }, currentTypingText.length * typingSpeed);
      }
    }
  };

  // Fonction pour basculer l'affichage de l'historique sur mobile
  const toggleHistory = () => {
    setShowHistory(!showHistory);
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-32 md:pt-36 lg:pt-40">
          <div className="flex justify-between items-center mb-6 md:mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              Max, le chatbot
            </h1>
            
            {/* Bouton pour l'historique sur mobile */}
            <button 
              className="history-toggle-button md:hidden"
              onClick={toggleHistory}
            >
              {showHistory ? 'Masquer l\'historique' : 'Afficher l\'historique'}
            </button>
          </div>
          
          <div className="flex flex-col md:flex-row">
            {/* Historique des conversations (sur desktop ou si affiché sur mobile) */}
            <div className={`chat-history-wrapper ${showHistory ? 'show' : 'hide'} md:block`}>
              <ChatHistory 
                onSelectConversation={initializeConversation}
                currentConversationId={conversationId}
              />
            </div>
            
            {/* Interface principale du chatbot */}
            <div className="chatbot-container flex-1">
              {/* Zone d'affichage des messages */}
              <div className="messages-container">
                {messages.map((message) => (
                  <div 
                    key={message.id} 
                    className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}
                               ${message.error ? 'error-message' : ''}
                               ${message.isThinking ? 'thinking-message' : ''}`}
                  >
                    {message.sender === 'user' ? (
                      message.text
                    ) : message.isThinking ? (
                      <div className="thinking-indicator">
                        <div className="thinking-text">{message.text}</div>
                        <div className="thinking-animation">
                          <span></span><span></span><span></span>
                        </div>
                      </div>
                    ) : (
                      <div className="markdown-content">
                        <ReactMarkdown>{message.text}</ReactMarkdown>
                      </div>
                    )}
                    {message.metadata && !message.isThinking && (
                      <div className="message-metadata">
                        <small>Modèle: {message.metadata.model} | Temps: {message.metadata.processingTime?.toFixed(2)}s</small>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Effet de frappe pendant la génération de la réponse */}
                {isTyping && (
                  <div className="message bot-message">
                    <div className="markdown-content">
                      <TypeAnimation
                        sequence={[currentTypingText]}
                        wrapper="div"
                        cursor={true}
                        repeat={0}
                        speed={90}
                        style={{ whiteSpace: 'pre-line', display: 'block' }}
                      />
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
                  disabled={isLoading || isTyping}
                />
                <button 
                  type="submit" 
                  className={`send-button ${isLoading || isTyping ? 'disabled' : ''}`}
                  disabled={isLoading || isTyping}
                >
                  {isLoading || isTyping ? 'Envoi...' : 'Envoyer'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;