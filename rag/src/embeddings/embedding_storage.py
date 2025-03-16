# src/embeddings/embedding_storage.py
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from src.storage.supabase_client import get_supabase_client

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingStorage:
    """
    Classe pour gérer le stockage et la récupération des embeddings dans Supabase.
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de stockage d'embeddings.
        """
        self.supabase = get_supabase_client()
        logger.info("Gestionnaire de stockage d'embeddings initialisé")
    
    def store_page_embedding(self, page_id: int, embedding: List[float]) -> bool:
        """
        Stocke l'embedding d'une page dans Supabase.
        
        Args:
            page_id (int): ID de la page.
            embedding (List[float]): Embedding de la page.
            
        Returns:
            bool: True si l'embedding a été stocké avec succès, False sinon.
        """
        try:
            # Préparer les données à insérer
            data = {
                "page_id": page_id,
                # Assurez-vous que l'embedding est envoyé sous forme de liste Python
                "embedding": embedding
            }
            
            # Insérer l'embedding dans la table page_embeddings
            result = self.supabase.table("page_embeddings").insert(data).execute()
            
            if result.data and len(result.data) > 0:
                embedding_id = result.data[0]['id']
                logger.info(f"Embedding stocké avec succès pour la page {page_id} avec l'ID {embedding_id}")
                return True
            else:
                logger.warning(f"Impossible de récupérer l'ID pour l'embedding de la page {page_id}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du stockage de l'embedding pour la page {page_id}: {str(e)}")
            return False
    
    def get_page_embedding(self, page_id: int) -> Optional[List[float]]:
        """
        Récupère l'embedding d'une page depuis Supabase.
        
        Args:
            page_id (int): ID de la page.
            
        Returns:
            Optional[List[float]]: Embedding de la page ou None si non trouvé.
        """
        try:
            # Récupérer l'embedding depuis la table page_embeddings
            result = self.supabase.table("page_embeddings").select("embedding").eq("page_id", page_id).execute()
            
            if result.data and len(result.data) > 0:
                embedding = result.data[0]['embedding']
                logger.info(f"Embedding récupéré avec succès pour la page {page_id}")
                return embedding
            else:
                logger.warning(f"Aucun embedding trouvé pour la page {page_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'embedding pour la page {page_id}: {str(e)}")
            return None
    
    def find_similar_pages(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche les pages les plus similaires à une requête donnée.
        
        Args:
            query_embedding (List[float]): Embedding de la requête.
            top_k (int): Nombre de résultats à retourner.
            
        Returns:
            List[Dict[str, Any]]: Liste des pages similaires avec leurs scores.
        """
        try:
            # Exécuter la requête RPC pour calculer la similarité
            rpc_response = self.supabase.rpc(
                "match_page_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": top_k
                }
            ).execute()
            
            if rpc_response.data:
                logger.info(f"Recherche de similarité réussie, {len(rpc_response.data)} résultats trouvés")
                return rpc_response.data
            else:
                logger.warning("Aucun résultat trouvé pour la recherche de similarité")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de similarité: {str(e)}")
            return []


# Fonction pour obtenir une instance du gestionnaire de stockage d'embeddings
def get_embedding_storage() -> EmbeddingStorage:
    return EmbeddingStorage()