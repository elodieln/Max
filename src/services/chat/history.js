import { supabase } from '../../lib/supabase';
import { v4 as uuidv4 } from 'uuid';

// Utilisateur de test (à remplacer par l'authentification réelle)
const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr';

// Créer une nouvelle conversation
export const createConversation = () => {
  return uuidv4();
};

// Sauvegarder un message dans l'historique
export const saveMessage = async (message, conversationId) => {
  try {
    const { data, error } = await supabase
      .from('chat_history')
      .insert({
        user_email: TEST_USER_EMAIL,
        message_text: message.text,
        sender: message.sender,
        metadata: message.metadata || null,
        conversation_id: conversationId
      });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur lors de la sauvegarde du message:', error);
    throw error;
  }
};

// Charger l'historique d'une conversation
export const loadConversationHistory = async (conversationId) => {
  try {
    const { data, error } = await supabase
      .from('chat_history')
      .select('*')
      .eq('user_email', TEST_USER_EMAIL)
      .eq('conversation_id', conversationId)
      .order('timestamp', { ascending: true });

    if (error) throw error;
    
    // Transformer les données pour correspondre à la structure de messages de l'application
    return data.map(message => ({
      id: message.id,
      text: message.message_text,
      sender: message.sender,
      metadata: message.metadata
    }));
  } catch (error) {
    console.error('Erreur lors du chargement de l\'historique:', error);
    return [];
  }
};

// Obtenir la liste des conversations de l'utilisateur
export const getUserConversations = async () => {
  try {
    const { data, error } = await supabase
      .from('chat_history')
      .select('conversation_id, timestamp')
      .eq('user_email', TEST_USER_EMAIL)
      .order('timestamp', { ascending: false });

    if (error) throw error;
    
    // Obtenir les IDs uniques de conversation
    const uniqueConversations = [...new Set(data.map(item => item.conversation_id))];
    
    // Pour chaque conversation, récupérer le premier message comme titre
    const conversations = [];
    
    for (const conversationId of uniqueConversations) {
      const { data: firstMessage, error: firstMessageError } = await supabase
        .from('chat_history')
        .select('*')
        .eq('conversation_id', conversationId)
        .eq('user_email', TEST_USER_EMAIL)
        .eq('sender', 'user')
        .order('timestamp', { ascending: true })
        .limit(1);
        
      if (!firstMessageError && firstMessage.length > 0) {
        conversations.push({
          id: conversationId,
          title: firstMessage[0].message_text.substring(0, 30) + (firstMessage[0].message_text.length > 30 ? '...' : ''),
          timestamp: firstMessage[0].timestamp
        });
      }
    }
    
    return conversations;
  } catch (error) {
    console.error('Erreur lors de la récupération des conversations:', error);
    return [];
  }
};

// Fonction pour supprimer une conversation
export const deleteConversation = async (conversationId) => {
    try {
      const { error } = await supabase
        .from('chat_history')
        .delete()
        .eq('conversation_id', conversationId)
        .eq('user_email', TEST_USER_EMAIL);
  
      if (error) throw error;
      return { success: true };
    } catch (error) {
      console.error('Erreur lors de la suppression de la conversation:', error);
      throw error;
    }
  };