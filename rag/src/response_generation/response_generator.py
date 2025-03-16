"""
Module pour la génération de réponses éducatives.
Ce module contient les composants nécessaires pour générer des réponses
pédagogiques à partir de la recherche RAG et en utilisant différents LLMs via OpenRouter.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import sys
import os

from api.openrouter_client import get_openrouter_client
from search.rag_engine import get_rag_engine
from response_generation.prompt_engineering import get_prompt_builder

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Classe pour générer des réponses éducatives en utilisant les résultats du RAG
    et différents modèles de langage via OpenRouter.
    """
    
    def __init__(self):
        """
        Initialise le générateur de réponses.
        """
        self.openrouter_client = get_openrouter_client()
        self.rag_engine = get_rag_engine()
        self.prompt_builder = get_prompt_builder()
        
        # Paramètres par défaut pour la génération de réponses
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo-16k")
        self.default_temperature = 0.3  # Température basse pour des réponses plus déterministes
        self.default_max_tokens = 1500
        
        logger.info("Générateur de réponses initialisé")
    
    def generate_response(
        self, 
        query: str, 
        query_type: str = "question",
        model: Optional[str] = None, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Génère une réponse éducative à partir d'une requête.
        
        Args:
            query: La requête de l'utilisateur
            query_type: Le type de requête (question, cours, concept, json, problème)
            model: Le modèle à utiliser (par défaut: celui défini dans DEFAULT_MODEL)
            temperature: La température pour la génération (par défaut: 0.3)
            max_tokens: Le nombre maximum de tokens à générer
            metadata: Métadonnées supplémentaires pour le prompt
            
        Returns:
            Dictionnaire contenant la réponse et des métadonnées
        """
        start_time = time.time()
        logger.info(f"Génération de réponse pour la requête: {query}")
        
        # Utiliser les valeurs par défaut si non spécifiées
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        # Étape 1: Récupérer les informations pertinentes via le RAG
        rag_result = self.rag_engine.retrieve(query)
        
        # Extraire le contexte
        context = rag_result.get("context", "")
        
        # Extraire ou créer les métadonnées
        if metadata is None:
            metadata = {}
        
        # Ajouter les métadonnées du RAG si disponibles
        if "metadata" in rag_result:
            metadata.update(rag_result["metadata"])
        
        # Étape 2: Construire le prompt approprié
        prompt = self.prompt_builder.build_prompt(query_type, context, query, metadata)
        
        # Étape 3: Préparer les messages pour OpenRouter au format attendu
        messages = [
            {"role": "system", "content": "Vous êtes un assistant expert en électronique, spécialisé dans l'éducation pour les étudiants en école d'ingénieur."},
            {"role": "user", "content": prompt}
        ]
        
        # Étape 4: Appeler le LLM via OpenRouter
        try:
            response = self.openrouter_client.generate_response(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extraire le texte de la réponse du modèle
            response_text = self._extract_response_text(response)
            
            # Traiter la réponse selon le type de requête
            processed_response = self._process_response_by_type(response_text, query_type)
            
            # Calculer le temps de réponse
            processing_time = time.time() - start_time
            
            # Construire le résultat
            result = {
                "response": processed_response,
                "processing_time": processing_time,
                "model_used": model,
                "query_type": query_type,
                "status": "success"
            }
            
            # Ajouter des métadonnées supplémentaires si disponibles
            if "search_results" in rag_result:
                # Limiter le nombre de résultats à inclure
                result["search_results"] = rag_result["search_results"][:3]
                
            logger.info(f"Réponse générée en {processing_time:.2f} secondes avec le modèle {model}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse: {str(e)}")
            return {
                "response": "Je suis désolé, mais je n'ai pas pu générer une réponse à votre question. Veuillez réessayer.",
                "processing_time": time.time() - start_time,
                "model_used": model,
                "query_type": query_type,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """
        Extrait le texte de la réponse du modèle.
        
        Args:
            response: La réponse complète du modèle
            
        Returns:
            Le texte extrait
        """
        # Adapter selon le format de réponse d'OpenRouter
        try:
            if "choices" in response and len(response["choices"]) > 0:
                if "message" in response["choices"][0]:
                    return response["choices"][0]["message"]["content"]
                elif "text" in response["choices"][0]:
                    return response["choices"][0]["text"]
            return str(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte de la réponse: {str(e)}")
            return str(response)
    
    def _process_response_by_type(self, response_text: str, query_type: str) -> Union[str, Dict[str, Any]]:
        """
        Traite la réponse selon le type de requête.
        
        Args:
            response_text: Le texte brut de la réponse
            query_type: Le type de requête
            
        Returns:
            La réponse traitée, soit sous forme de texte, soit sous forme de dictionnaire
        """
        # Si le type est JSON, tenter de parser la réponse
        if query_type == "json":
            try:
                # Essayer d'extraire le JSON si la réponse contient du texte supplémentaire
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    # Parser le JSON
                    return json.loads(json_str)
                else:
                    logger.warning("Réponse JSON introuvable dans la réponse")
                    return response_text
            except json.JSONDecodeError as e:
                logger.error(f"Erreur lors du parsing JSON: {str(e)}")
                return response_text
        
        # Pour les autres types, retourner le texte brut
        return response_text

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des modèles disponibles via OpenRouter.
        
        Returns:
            Liste des modèles disponibles
        """
        try:
            models = self.openrouter_client.get_available_models()
            return models
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles disponibles: {str(e)}")
            return []

# Fonction pour obtenir une instance du générateur de réponses
def get_response_generator() -> ResponseGenerator:
    return ResponseGenerator()