# src/search/search_service.py
import logging
from typing import List, Dict, Any, Optional, Tuple
from src.embeddings.embedding_generator import get_embedding_generator
from src.embeddings.embedding_storage import get_embedding_storage
from src.storage.supabase_client import get_supabase_client

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchService:
    """
    Service de recherche basé sur les embeddings pour trouver les contenus les plus pertinents.
    """
    
    def __init__(self):
        """
        Initialise le service de recherche.
        """
        self.embedding_generator = get_embedding_generator()
        self.embedding_storage = get_embedding_storage()
        self.supabase = get_supabase_client()
        logger.info("Service de recherche initialisé")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sémantique basée sur une requête textuelle.
        
        Args:
            query (str): Requête textuelle.
            top_k (int): Nombre maximum de résultats à retourner.
            threshold (float): Seuil de similarité minimum (de 0 à 1).
            
        Returns:
            List[Dict[str, Any]]: Liste des résultats pertinents avec leurs métadonnées.
        """
        try:
            # Générer l'embedding pour la requête
            query_embedding = self.embedding_generator.generate_query_embedding(query)
            
            if not query_embedding:
                logger.error("Impossible de générer l'embedding pour la requête")
                return []
            
            # Rechercher les pages similaires
            similar_pages = self.search_with_embedding(query_embedding, top_k, threshold)
            
            return similar_pages
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            return []
    
    def search_with_embedding(self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sémantique basée sur un embedding.
        
        Args:
            query_embedding (List[float]): Embedding de la requête.
            top_k (int): Nombre maximum de résultats à retourner.
            threshold (float): Seuil de similarité minimum (de 0 à 1).
            
        Returns:
            List[Dict[str, Any]]: Liste des résultats pertinents avec leurs métadonnées.
        """
        try:
            # Rechercher les pages similaires via la fonction RPC
            similar_embeddings = self.supabase.rpc(
                "match_page_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": top_k
                }
            ).execute()
            
            if not similar_embeddings.data:
                logger.warning("Aucune page similaire trouvée")
                return []
            
            # Récupérer les informations détaillées des pages
            detailed_results = []
            
            for result in similar_embeddings.data:
                page_id = result.get('page_id')
                similarity = result.get('similarity')
                
                if not page_id:
                    continue
                
                # Récupérer les détails de la page
                page_details = self._get_page_details(page_id)
                
                if page_details:
                    # Ajouter le score de similarité
                    page_details['similarity'] = similarity
                    detailed_results.append(page_details)
            
            # Trier par similarité décroissante
            detailed_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            logger.info(f"Recherche terminée avec {len(detailed_results)} résultats pertinents")
            return detailed_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche avec embedding: {str(e)}")
            return []
    
    def _get_page_details(self, page_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'une page à partir de son ID.
        
        Args:
            page_id (int): ID de la page dans Supabase.
            
        Returns:
            Optional[Dict[str, Any]]: Détails de la page ou None si non trouvée.
        """
        try:
            # Récupérer les détails de la page avec une jointure sur le cours
            page_result = self.supabase.from_("pages").select(
                "id, page_number, image_path, content_text, courses(id, name, year)"
            ).eq("id", page_id).execute()
            
            if page_result.data and len(page_result.data) > 0:
                return page_result.data[0]
            else:
                logger.warning(f"Page non trouvée avec l'ID: {page_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails de la page {page_id}: {str(e)}")
            return None

# Fonction pour obtenir une instance du service de recherche
def get_search_service() -> SearchService:
    return SearchService()