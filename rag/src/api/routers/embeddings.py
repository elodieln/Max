# src/api/routers/embeddings.py
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from embeddings.embedding_generator import get_embedding_generator
from embeddings.embedding_storage import get_embedding_storage
from search.search_service import get_search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/embeddings")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    threshold: float = 0.5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    query: str

@router.post("/search", response_model=SearchResponse)
async def search_embeddings(request: SearchRequest):
    """
    Recherche les pages les plus pertinentes pour une requête textuelle.
    """
    try:
        logger.info(f"Recherche d'embeddings pour la requête: {request.query}")
        
        # Obtenir le service de recherche
        search_service = get_search_service()
        
        # Effectuer la recherche
        results = search_service.search(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return {
            "results": results,
            "count": len(results),
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche d'embeddings: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_embedding_stats():
    """
    Récupère des statistiques sur les embeddings stockés.
    """
    try:
        supabase = get_embedding_storage().supabase
        
        # Obtenir le nombre total d'embeddings
        count_query = supabase.table("page_embeddings").select("count", count="exact").execute()
        total_count = count_query.count if hasattr(count_query, 'count') else 0
        
        # Obtenir le nombre de pages avec embeddings par cours
        stats_query = supabase.from_("page_embeddings").select(
            "pages(course_id)",
            count="exact"
        ).execute()
        
        return {
            "total_embeddings": total_count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques d'embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")