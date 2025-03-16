import os
import json
import requests
from dotenv import load_dotenv
import logging


# Charger les variables d'environnement
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("La variable d'environnement OPENROUTER_API_KEY doit être définie")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo-16k")
    
    def get_available_models(self):
        """Récupère la liste des modèles disponibles sur OpenRouter"""
        try:
            url = f"{self.base_url}/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Analyser la réponse
            data = response.json()
            
            # Vérifier le format et normaliser
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                return data["data"]
            elif isinstance(data, dict) and "models" in data and isinstance(data["models"], list):
                return data["models"]
            else:
                # Retourner le dictionnaire tel quel
                return data
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles disponibles: {str(e)}")
            # Retourner une liste vide en cas d'erreur plutôt que de laisser l'erreur se propager
            return []
    
    def generate_response(self, messages, model=None, temperature=0.7, max_tokens=1000):
        """Génère une réponse à partir des messages en utilisant le modèle spécifié"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Utiliser le modèle par défaut si aucun n'est spécifié
        model = model or self.default_model
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

# Fonction pour obtenir une instance du client OpenRouter
def get_openrouter_client():
    return OpenRouterClient()