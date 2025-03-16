# src/api/routers/queries.py
import logging
import time
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from response_generation.response_generator import get_response_generator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/queries")

class QueryRequest(BaseModel):
    query: str = Field(..., description="La requête de l'utilisateur")
    query_type: str = Field("question", description="Type de requête (question, json, concept, cours, probleme)")
    model: Optional[str] = Field(None, description="Modèle LLM à utiliser (optionnel)")
    temperature: float = Field(0.3, description="Température pour la génération (0.0-1.0)")

class QueryResponse(BaseModel):
    response: Any
    processing_time: float
    model_used: str
    query_type: str
    status: str
    search_results: Optional[List[Dict[str, Any]]] = None

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Répond à une question en utilisant le système RAG multimodal.
    """
    start_time = time.time()
    logger.info(f"Requête reçue: {request.query} (type: {request.query_type})")
    
    try:
        # Obtenir le générateur de réponses
        response_generator = get_response_generator()
        
        # Générer la réponse
        result = response_generator.generate_response(
            query=request.query,
            query_type=request.query_type,
            model=request.model,
            temperature=request.temperature
        )
        
        # Calculer le temps de traitement total
        result["processing_time"] = time.time() - start_time
        
        logger.info(f"Réponse générée en {result['processing_time']:.2f} secondes")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@router.get("/models", response_model=List[Dict[str, Any]])
async def list_models():
    """
    Liste les modèles LLM disponibles via OpenRouter.
    """
    try:
        response_generator = get_response_generator()
        models_data = response_generator.get_available_models()
        
        # Vérifier et traiter la réponse
        if isinstance(models_data, list):
            models = models_data
        elif isinstance(models_data, dict) and "data" in models_data and isinstance(models_data["data"], list):
            # Si la réponse est un dictionnaire avec une clé 'data' contenant une liste
            models = models_data["data"]
        elif isinstance(models_data, dict) and "models" in models_data and isinstance(models_data["models"], list):
            # Si la réponse est un dictionnaire avec une clé 'models' contenant une liste
            models = models_data["models"]
        else:
            # Dernière option, retourner un tableau avec le dictionnaire entier ou vide
            if isinstance(models_data, dict):
                # Convertir en liste de modèles si possible
                models = [{"id": k, "name": k, "details": v} for k, v in models_data.items() if isinstance(v, dict)]
                if not models:
                    # Si conversion échouée, ajouter le dictionnaire entier comme un seul élément
                    models = [{"id": "default", "details": models_data}]
            else:
                # Retourner une liste vide
                models = []
                
        logger.info(f"Récupération de {len(models)} modèles réussie")
        return models
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des modèles: {str(e)}")