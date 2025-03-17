import React, { useState } from 'react';
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
  
  // Fonction pour gérer l'envoi d'un message
  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    
    // Ajouter le message de l'utilisateur à la liste des messages
    const newUserMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user'
    };
    
    setMessages([...messages, newUserMessage]);
    setInputMessage('');
    
    // Note: La réponse du bot sera implémentée dans le Sprint 2
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
                  className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
                >
                  {message.text}
                </div>
              ))}
            </div>
            
            {/* Formulaire de saisie */}
            <form onSubmit={handleSendMessage} className="message-form">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Posez votre question sur l'électronique..."
                className="message-input"
              />
              <button type="submit" className="send-button">
                Envoyer
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;