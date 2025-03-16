# src/embeddings/embedding_generator.py
import os
import logging
from typing import List, Dict, Any, Optional
from src.embeddings.multimodal_embeddings import get_multimodal_embeddings_client
from src.embeddings.embedding_storage import get_embedding_storage
from src.utils.image_utils import optimize_image_for_embeddings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Classe pour générer et stocker des embeddings pour les pages des cours.
    """
    
    def __init__(self):
        """
        Initialise le générateur d'embeddings.
        """
        self.embeddings_client = get_multimodal_embeddings_client()
        self.storage = get_embedding_storage()
        logger.info("Générateur d'embeddings initialisé")
    
    def generate_and_store_embeddings(self, pages_info: List[Dict[str, Any]]) -> List[int]:
        """
        Génère et stocke les embeddings pour une liste de pages.
        
        Args:
            pages_info (List[Dict[str, Any]]): Liste des informations de pages.
                Chaque dictionnaire doit contenir:
                - id (int): ID de la page dans Supabase
                - image_path (str): Chemin vers l'image de la page
                
        Returns:
            List[int]: Liste des IDs des pages pour lesquelles les embeddings ont été générés avec succès.
        """
        try:
            successful_ids = []
            
            # Optimiser les images pour la génération d'embeddings
            optimized_image_paths = []
            page_ids = []
            
            for page_info in pages_info:
                page_id = page_info.get('id')
                image_path = page_info.get('image_path')
                
                if not page_id or not image_path:
                    logger.warning(f"Données de page incomplètes: {page_info}")
                    continue
                
                if not os.path.exists(image_path):
                    logger.warning(f"L'image n'existe pas: {image_path}")
                    continue
                
                # Optimiser l'image
                optimized_path = optimize_image_for_embeddings(image_path)
                optimized_image_paths.append(optimized_path)
                page_ids.append(page_id)
            
            if not optimized_image_paths:
                logger.warning("Aucune image valide trouvée pour générer des embeddings")
                return []
            
            # Générer les embeddings par lots de 10 images maximum
            batch_size = 10
            for i in range(0, len(optimized_image_paths), batch_size):
                batch_paths = optimized_image_paths[i:i + batch_size]
                batch_ids = page_ids[i:i + batch_size]
                
                logger.info(f"Génération d'embeddings pour le lot {i//batch_size + 1}/{(len(optimized_image_paths) + batch_size - 1)//batch_size}")
                
                # Générer les embeddings
                embeddings = self.embeddings_client.encode_documents(batch_paths)
                
                # Stocker les embeddings
                for j, (page_id, embedding) in enumerate(zip(batch_ids, embeddings)):
                    success = self.storage.store_page_embedding(page_id, embedding)
                    if success:
                        successful_ids.append(page_id)
                        logger.info(f"Embedding stocké avec succès pour la page {page_id} ({j+1}/{len(batch_ids)})")
                    else:
                        logger.warning(f"Échec du stockage de l'embedding pour la page {page_id}")
            
            return successful_ids
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération et du stockage des embeddings: {str(e)}")
            return []
    
    def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """
        Génère un embedding pour une requête textuelle.
        
        Args:
            query (str): Requête textuelle.
            
        Returns:
            Optional[List[float]]: Embedding de la requête ou None en cas d'erreur.
        """
        try:
            # Générer l'embedding
            embeddings = self.embeddings_client.encode_queries([query])
            
            if embeddings and len(embeddings) > 0:
                logger.info(f"Embedding généré avec succès pour la requête: {query[:50]}...")
                return embeddings[0]
            else:
                logger.warning(f"Aucun embedding généré pour la requête: {query[:50]}...")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'embedding pour la requête: {str(e)}")
            return None


# Fonction pour obtenir une instance du générateur d'embeddings
def get_embedding_generator() -> EmbeddingGenerator:
    return EmbeddingGenerator()