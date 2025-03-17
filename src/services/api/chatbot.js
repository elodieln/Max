import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Fonction pour envoyer une question à Max et obtenir une réponse
export const askQuestion = async (query, queryType = 'question') => {
  try {
    const response = await axios.post(`${API_BASE_URL}/queries/ask`, {
      query,
      query_type: queryType,
      temperature: 0.3
    });
    
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la requête vers l\'API:', error);
    throw error;
  }
};

// Fonction pour vérifier la santé de l'API
export const checkApiHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data.status === 'healthy';
  } catch (error) {
    console.error('Erreur lors de la vérification de l\'état de l\'API:', error);
    return false;
  }
};