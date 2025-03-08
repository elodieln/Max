# src/embeddings/embeddings_client.py
import requests
import json
import base64
import io
import logging
import tempfile
from typing import List, Dict, Any, Union
from PIL import Image
import os
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingsClient:
    """Client pour générer des embeddings à partir de texte et d'images"""
    
    def __init__(self):
        self.base_url = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
        self.dimension = 1536  # Dimension par défaut des embeddings
        
        # Modèle local pour le texte
        self.text_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        logger.info("Initialized EmbeddingsClient")
        
    async def encode_text(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de textes en utilisant l'API distante
        
        Args:
            texts: Liste de chaînes de texte
            
        Returns:
            Liste d'embeddings
        """
        try:
            # Utiliser l'API distante
            url = f"{self.base_url}/encode_queries"
            
            # Envoyer directement la liste des textes
            response = requests.post(
                url,
                json=texts,  # Envoyer directement la liste
                params={"dimension": self.dimension}
            )
            
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}, {response.text}")
                
            embeddings = response.json()["embeddings"]
            logger.info(f"Successfully generated {len(embeddings)} text embeddings via API")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating text embeddings: {str(e)}")
            
            # Fallback sur le modèle local
            logger.info("Falling back to local model")
            local_embeddings = self.text_model.encode(texts, convert_to_numpy=True)
            
            # Adapter les dimensions : répéter l'embedding jusqu'à atteindre la taille requise
            adapted_embeddings = []
            for emb in local_embeddings:
                # Calculer combien de fois nous devons répéter l'embedding
                repetitions = self.dimension // len(emb) + 1
                # Répéter et tronquer à la taille exacte requise
                extended_emb = np.tile(emb, repetitions)[:self.dimension].tolist()
                adapted_embeddings.append(extended_emb)
                
            logger.info(f"Successfully generated {len(adapted_embeddings)} text embeddings locally")
            return adapted_embeddings
    
    async def encode_images(self, image_data_list: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste d'images en base64
        
        Args:
            image_data_list: Liste de chaînes base64 représentant des images
            
        Returns:
            Liste d'embeddings (vecteurs de dimension 1536)
        """
        try:
            url = f"{self.base_url}/encode_documents"
            
            # Créer des fichiers temporaires à partir des données base64
            temp_files = []
            files = []
            
            for idx, img_base64 in enumerate(image_data_list):
                try:
                    # Décoder le base64
                    img_data = base64.b64decode(img_base64)
                    
                    # Créer un fichier temporaire
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(img_data)
                    temp_file.close()
                    temp_files.append(temp_file.name)
                    
                    # Ajouter à la liste de fichiers pour la requête
                    files.append(
                        ('files', (f'image_{idx}.png', open(temp_file.name, 'rb'), 'image/png'))
                    )
                except Exception as e:
                    logger.error(f"Error processing image {idx}: {str(e)}")
                    # Continuer avec les autres images
            
            if not files:
                logger.error("No valid images to process")
                return []
                
            logger.info(f"Generating embeddings for {len(files)} images")
            response = requests.post(
                url, 
                files=files, 
                params={"dimension": self.dimension}
            )
            
            # Nettoyer les fichiers temporaires
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
            
            if response.status_code == 200:
                embeddings = response.json()["embeddings"]
                logger.info(f"Successfully generated {len(embeddings)} image embeddings")
                return embeddings
            else:
                # En cas d'erreur, retourner des embeddings vides
                logger.error(f"Error: {response.status_code}, {response.text}")
                return [[0] * self.dimension for _ in range(len(files))]
                
        except Exception as e:
            logger.error(f"Error generating image embeddings: {str(e)}")
            # Retourner des embeddings vides en cas d'erreur
            return [[0] * self.dimension for _ in range(len(image_data_list))]
    
    async def compute_similarity(self, query_embedding: List[float], doc_embedding: List[float]) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings
        
        Args:
            query_embedding: Embedding de la requête
            doc_embedding: Embedding du document
            
        Returns:
            Score de similarité (0-1)
        """
        try:
            query_vec = np.array(query_embedding)
            doc_vec = np.array(doc_embedding)
            
            # Normalisation des vecteurs
            query_norm = np.linalg.norm(query_vec)
            doc_norm = np.linalg.norm(doc_vec)
            
            if query_norm == 0 or doc_norm == 0:
                return 0
                
            # Similarité cosinus
            similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0