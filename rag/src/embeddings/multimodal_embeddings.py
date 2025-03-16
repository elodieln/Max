# src/embeddings/multimodal_embeddings.py
import os
import requests
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultimodalEmbeddingsClient:
    """
    Client pour générer des embeddings multimodaux à partir de textes et d'images
    en utilisant l'API RAG Multimodal.
    """
    
    def __init__(self, base_url: str = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"):
        """
        Initialise le client d'embeddings multimodal.
        
        Args:
            base_url (str): URL de base de l'API d'embeddings.
        """
        self.base_url = base_url
        logger.info(f"Client d'embeddings multimodal initialisé avec l'URL: {base_url}")
    
    def encode_queries(self, queries: List[str], dimension: int = 1536) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de requêtes textuelles.
        
        Args:
            queries (List[str]): Liste des requêtes textuelles.
            dimension (int): Dimension des embeddings à générer.
            
        Returns:
            List[List[float]]: Liste des embeddings générés.
        """
        try:
            url = f"{self.base_url}/encode_queries"
            
            # Vérifier que queries est bien une liste
            if not isinstance(queries, list):
                queries = [queries]
                
            # Important: L'API attend directement la liste de requêtes, pas un dict
            logger.info(f"Envoi de {len(queries)} requêtes à {url}")
            
            response = requests.post(
                url,
                json=queries,  # Envoi direct de la liste
                params={"dimension": dimension}
            )
            
            if response.status_code == 200:
                embeddings = response.json()["embeddings"]
                logger.info(f"Embeddings générés avec succès pour {len(queries)} requêtes")
                return embeddings
            else:
                logger.error(f"Erreur lors de la génération des embeddings: {response.status_code}, {response.text}")
                raise Exception(f"Erreur: {response.status_code}, {response.text}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'encodage des requêtes: {str(e)}")
            raise
    
    def encode_documents(self, image_paths: List[str], dimension: int = 1536) -> List[List[float]]:
        """
        Génère des embeddings pour une liste d'images.
        
        Args:
            image_paths (List[str]): Liste des chemins vers les images.
            dimension (int): Dimension des embeddings à générer.
            
        Returns:
            List[List[float]]: Liste des embeddings générés.
        """
        try:
            url = f"{self.base_url}/encode_documents"
            
            files = []
            open_files = []  # Pour garder une référence aux fichiers ouverts
            
            for path in image_paths:
                # Vérifier que le fichier existe
                if not os.path.exists(path):
                    logger.error(f"L'image n'existe pas: {path}")
                    raise FileNotFoundError(f"L'image n'existe pas: {path}")
                
                # Récupérer le nom du fichier
                file_name = Path(path).name
                
                # Ouvrir le fichier et garder une référence
                file_obj = open(path, 'rb')
                open_files.append(file_obj)
                
                # Ajouter le fichier à la liste
                files.append(('files', (file_name, file_obj, 'image/jpeg')))
            
            logger.info(f"Envoi de la requête à {url} avec {len(files)} fichiers")
            
            response = requests.post(
                url,
                files=files,
                params={"dimension": dimension}
            )
            
            # Fermer tous les fichiers ouverts
            for file_obj in open_files:
                file_obj.close()
            
            if response.status_code == 200:
                embeddings = response.json()["embeddings"]
                logger.info(f"Embeddings générés avec succès pour {len(image_paths)} images")
                return embeddings
            else:
                logger.error(f"Erreur lors de la génération des embeddings: {response.status_code}, {response.text}")
                # Ajoutons plus de détails sur la requête pour faciliter le débogage
                logger.error(f"Détails de la requête: URL={url}, Fichiers={[p for p in image_paths]}")
                raise Exception(f"Erreur: {response.status_code}, {response.text}")
                
        except Exception as e:
            # S'assurer que tous les fichiers sont fermés même en cas d'erreur
            for file_obj in open_files if 'open_files' in locals() else []:
                try:
                    file_obj.close()
                except:
                    pass
            
            logger.error(f"Erreur lors de l'encodage des documents: {str(e)}")
            raise
    
    @staticmethod
    def compute_similarity(query_embedding: List[float], doc_embedding: List[float]) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.
        
        Args:
            query_embedding (List[float]): Embedding de la requête.
            doc_embedding (List[float]): Embedding du document.
            
        Returns:
            float: Score de similarité.
        """
        return np.dot(query_embedding, doc_embedding)


# Fonction pour obtenir une instance du client d'embeddings multimodal
def get_multimodal_embeddings_client() -> MultimodalEmbeddingsClient:
    return MultimodalEmbeddingsClient()