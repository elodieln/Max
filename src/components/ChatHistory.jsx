import React, { useState, useEffect } from 'react';
import { getUserConversations, deleteConversation } from '../services/chat/history';
import { FiTrash2, FiChevronRight, FiMessageCircle, FiPlus } from 'react-icons/fi';
import './ChatHistory.css';

const ChatHistory = ({ onSelectConversation, currentConversationId }) => {
  const [conversations, setConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(null);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const userConversations = await getUserConversations();
      setConversations(userConversations);
    } catch (error) {
      console.error('Erreur lors du chargement des conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [currentConversationId]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Si c'est aujourd'hui, afficher "Aujourd'hui à HH:MM"
    if (date.toDateString() === now.toDateString()) {
      return `Aujourd'hui à ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
    }
    
    // Si c'est hier, afficher "Hier à HH:MM"
    if (date.toDateString() === yesterday.toDateString()) {
      return `Hier à ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
    }
    
    // Sinon, afficher la date complète
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDeleteConversation = async (e, conversationId) => {
    e.stopPropagation(); // Empêcher le clic de propager à l'élément parent
    
    if (confirmDelete === conversationId) {
      try {
        await deleteConversation(conversationId);
        // Si la conversation supprimée est celle actuellement affichée, créer une nouvelle conversation
        if (conversationId === currentConversationId) {
          onSelectConversation(null);
        }
        // Rafraîchir la liste des conversations
        loadConversations();
        setConfirmDelete(null);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    } else {
      // Demander confirmation
      setConfirmDelete(conversationId);
      
      // Réinitialiser l'état de confirmation après 3 secondes
      setTimeout(() => {
        setConfirmDelete(null);
      }, 3000);
    }
  };

  const filteredConversations = searchTerm
    ? conversations.filter(conv => 
        conv.title.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : conversations;

  return (
    <div className="chat-history-container">
      <h2 className="chat-history-title">
        <FiMessageCircle className="history-icon" />
        Historique des conversations
      </h2>
      
      <div className="search-container">
        <input
          type="text"
          placeholder="Rechercher une conversation..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="history-search-input"
        />
      </div>
      
      {isLoading ? (
        <div className="chat-history-loading">
          <div className="loading-spinner"></div>
          <span>Chargement...</span>
        </div>
      ) : filteredConversations.length === 0 ? (
        <div className="chat-history-empty">
          {searchTerm ? 'Aucun résultat trouvé' : 'Aucune conversation disponible'}
        </div>
      ) : (
        <ul className="conversation-list">
          {filteredConversations.map((conversation) => (
            <li 
              key={conversation.id}
              className={`conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="conversation-content">
                <div className="conversation-title">{conversation.title}</div>
                <div className="conversation-date">{formatDate(conversation.timestamp)}</div>
              </div>
              <button 
                className={`delete-button ${confirmDelete === conversation.id ? 'confirm-delete' : ''}`}
                onClick={(e) => handleDeleteConversation(e, conversation.id)}
                aria-label="Supprimer la conversation"
              >
                {confirmDelete === conversation.id ? 'Confirmer' : <FiTrash2 />}
              </button>
              <FiChevronRight className="chevron-icon" />
            </li>
          ))}
        </ul>
      )}
      
      <button 
        className="new-conversation-button"
        onClick={() => onSelectConversation(null)}
      >
        <FiPlus className="button-icon" />
        Nouvelle conversation
      </button>
    </div>
  );
};

export default ChatHistory;