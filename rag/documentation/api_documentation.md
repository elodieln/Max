Documentation de l'API Max RAG Multimodal

Cette documentation présente les endpoints disponibles dans l'API Max RAG Multimodal, un assistant IA conçu pour aider les élèves en école d'ingénieur en électronique.

Base URL
http://localhost:8000
En production, l'URL de base sera définie par votre déploiement.


Authentification
Actuellement, l'API ne nécessite pas d'authentification. Pour la mise en production, il est recommandé d'ajouter un système d'authentification.


Endpoints


Santé de l'API
GET /health
Vérifie que l'API est opérationnelle.
Réponse:
{
  "status": "healthy",
  "version": "1.0.0",
  "api_name": "Max RAG Multimodal API"
}


Requêtes
POST /queries/ask
Envoie une question à Max et reçoit une réponse générée avec le RAG multimodal.
Corps de la requête:
{
  "query": "Qu'est-ce qu'un condensateur?",
  "query_type": "question",
  "model": "gpt-3.5-turbo-16k",
  "temperature": 0.3
}


Paramètres:

query (obligatoire): La question à poser
query_type (optionnel): Type de requête. Valeurs possibles:

question: Question générale (par défaut)
json: Générer une fiche de cours au format JSON
concept: Expliquer un concept spécifique
cours: Générer un résumé de cours
probleme: Résoudre un problème électronique


model (optionnel): Modèle LLM à utiliser (laissez vide pour utiliser le modèle par défaut)
temperature (optionnel): Température pour la génération (0.0-1.0)

Réponse:
{
  "response": "Un condensateur est un composant électronique passif qui stocke l'énergie sous forme de champ électrique...",
  "processing_time": 2.5,
  "model_used": "gpt-3.5-turbo-16k",
  "query_type": "question",
  "status": "success",
  "search_results": [
    {
      "id": 42,
      "page_number": 12,
      "similarity": 0.89,
      "courses": {
        "id": 3,
        "name": "Électronique fondamentale"
      }
    }
  ]
}


GET /queries/models
Liste les modèles LLM disponibles via OpenRouter.
Réponse:
[
  {
    "id": "gpt-3.5-turbo-16k",
    "name": "GPT-3.5 Turbo 16k",
    "context_length": 16385,
    "pricing": {
      "prompt": 0.0000015,
      "completion": 0.000002
    }
  },
  {
    "id": "gpt-4",
    "name": "GPT-4",
    "context_length": 8192,
    "pricing": {
      "prompt": 0.00003,
      "completion": 0.00006
    }
  }
]


Documents
POST /documents/process
Traite un document PDF pour l'extraction et la génération d'embeddings.
Requête:

file (obligatoire): Fichier PDF à traiter
course_id (optionnel): ID du cours existant auquel associer le document
course_name (optionnel): Nom du nouveau cours à créer (si course_id n'est pas fourni)
year (optionnel): Année du cours (ING1, ING2, ING3), par défaut ING1
Réponse:
{
  "course_id": 5,
  "pages_processed": 42,
  "embeddings_generated": 42,
  "success": true,
  "message": "Document traité avec succès. 42 pages extraites, 42 embeddings générés."
}


GET /documents/courses
Liste tous les cours disponibles.
Réponse:
[
  {
    "id": 5,
    "name": "Électronique fondamentale",
    "pdf_url": "electronique_fondamentale.pdf",
    "photo_url": null,
    "year": "ING1",
    "created_at": "2023-11-15T14:30:00"
  }
]

Embeddings
POST /embeddings/search
Recherche les pages les plus pertinentes pour une requête.
Corps de la requête:
{
  "query": "Qu'est-ce qu'un condensateur?",
  "top_k": 5,
  "threshold": 0.5
}

Paramètres:

query (obligatoire): La requête de recherche
top_k (optionnel): Nombre de résultats à retourner, par défaut 5
threshold (optionnel): Seuil de similarité minimum (0.0-1.0), par défaut 0.5

Réponse:
{
  "results": [
    {
      "id": 42,
      "page_number": 12,
      "image_path": "data/images/course_5/page_12.png",
      "content_text": "Le condensateur est un composant électronique...",
      "similarity": 0.89,
      "courses": {
        "id": 5,
        "name": "Électronique fondamentale",
        "year": "ING1"
      }
    }
  ],
  "count": 1,
  "query": "Qu'est-ce qu'un condensateur?"
}

GET /embeddings/stats
Récupère des statistiques sur les embeddings stockés.
Réponse:
{
  "total_embeddings": 156,
  "status": "success"
}


Codes d'erreur

400: Requête invalide (paramètres manquants ou invalides)
404: Ressource non trouvée
500: Erreur interne du serveur

Gestion des erreurs
Toutes les erreurs suivent le format standard de FastAPI :
{
  "detail": "Description de l'erreur"
}


Limites

Taille maximale des fichiers PDF : 10 Mo
Limite de requêtes : 60 par minute
Nombre maximum de résultats de recherche : 20

Intégration avec le frontend
Pour intégrer cette API avec votre frontend Vite, vous pouvez utiliser Axios ou Fetch API. Voici un exemple avec Axios :
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Poser une question à Max
async function askQuestion(query, queryType = 'question') {
  try {
    const response = await axios.post(`${API_BASE_URL}/queries/ask`, {
      query,
      query_type: queryType,
      temperature: 0.3
    });
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la requête:', error);
    throw error;
  }
}

// Télécharger et traiter un document PDF
async function processDocument(file, courseName, year = 'ING1') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('course_name', courseName);
  formData.append('year', year);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/documents/process`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Erreur lors du traitement du document:', error);
    throw error;
  }
}

// Rechercher des contenus pertinents
async function searchContent(query, topK = 5) {
  try {
    const response = await axios.post(`${API_BASE_URL}/embeddings/search`, {
      query,
      top_k: topK,
      threshold: 0.5
    });
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la recherche:', error);
    throw error;
  }
}

// Récupérer la liste des cours
async function getCourses() {
  try {
    const response = await axios.get(`${API_BASE_URL}/documents/courses`);
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération des cours:', error);
    throw error;
  }
}

// Vérifier l'état de l'API
async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data.status === 'healthy';
  } catch (error) {
    console.error('Erreur lors de la vérification de l\'état de l\'API:', error);
    return false;
  }
}



Exemple d'utilisation dans un composant Vue (pour Vite)
<template>
  <div class="max-container">
    <h1>Assistant Max</h1>
    
    <div class="search-container">
      <input 
        v-model="question" 
        placeholder="Posez votre question sur l'électronique..." 
        @keyup.enter="askMax"
      />
      <button @click="askMax" :disabled="loading">Demander à Max</button>
    </div>
    
    <div v-if="loading" class="loading">
      Réflexion en cours...
    </div>
    
    <div v-if="response" class="response">
      <h2>Réponse de Max:</h2>
      <div v-html="formattedResponse"></div>
      
      <div class="meta-info">
        <p>Modèle utilisé: {{ response.model_used }}</p>
        <p>Temps de traitement: {{ response.processing_time.toFixed(2) }} secondes</p>
      </div>
    </div>
    
    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import { marked } from 'marked';

const API_BASE_URL = 'http://localhost:8000';
const question = ref('');
const response = ref(null);
const loading = ref(false);
const error = ref('');

// Formatage de la réponse en HTML (conversion Markdown)
const formattedResponse = computed(() => {
  if (!response.value || !response.value.response) return '';
  return marked(response.value.response);
});

// Fonction pour poser une question à Max
const askMax = async () => {
  if (!question.value.trim()) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const result = await axios.post(`${API_BASE_URL}/queries/ask`, {
      query: question.value,
      query_type: 'question',
      temperature: 0.3
    });
    
    response.value = result.data;
  } catch (err) {
    error.value = `Erreur: ${err.response?.data?.detail || err.message}`;
    response.value = null;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.max-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-container {
  display: flex;
  margin-bottom: 20px;
}

input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px 0 0 4px;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
}

.loading {
  margin: 20px 0;
  font-style: italic;
}

.response {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 4px solid #4CAF50;
}

.meta-info {
  margin-top: 15px;
  font-size: 14px;
  color: #666;
}

.error {
  margin-top: 20px;
  padding: 15px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
}
</style>


Déploiement
Pour déployer l'API en production, vous pouvez utiliser Docker ou des services comme Google Cloud Run, AWS Lambda, ou Heroku. Voici un exemple simple de configuration Docker :
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "src/main_api.py"]


Pour les besoins spécifiques de l'équipe frontend, n'hésitez pas à demander des ajustements ou des fonctionnalités supplémentaires à l'API.