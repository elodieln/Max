# src/database/supabase_client.py
import os
from supabase import create_client
import logging
from typing import List, Dict, Any
import json
from src.utils.custom_logging import log_progress

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_KEY')
            if not url or not key:
                raise ValueError("Missing Supabase credentials")
                
            self.supabase = create_client(url, key)
            logger.info("Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            raise

    async def get_courses(self):
        """Récupère tous les cours"""
        try:
            response = self.supabase.table('courses').select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching courses: {str(e)}")
            raise

    async def get_vectors_by_course_id(self, course_id: int):
        """Récupère les vecteurs pour un cours spécifique"""
        try:
            response = self.supabase.table('vectors')\
                .select("*")\
                .eq('course_id', course_id)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching vectors for course {course_id}: {str(e)}")
            raise

    async def get_course_id(self, course_name: str) -> int:
        """Récupère l'ID d'un cours existant par son nom"""
        try:
            response = self.supabase.table('courses')\
                .select("id")\
                .eq('name', course_name)\
                .execute()
                
            if not response.data:
                raise ValueError(f"Course '{course_name}' not found in database")
                
            return response.data[0]['id']
                
        except Exception as e:
            logger.error(f"Failed to get course ID: {str(e)}")
            raise

    async def store_chunks_with_embeddings(self, course_name: str, chunks: List[Dict[str, Any]], embeddings_client):
        """
        Stocke les chunks avec leurs embeddings dans Supabase
        Supporte désormais les chunks mixtes (texte + image)
        """
        try:
            course_id = await self.get_course_id(course_name)
            
            # Traiter les chunks par type
            text_chunks = []
            image_chunks = []
            mixed_chunks = []
            
            # Grouper les chunks par type
            for chunk in chunks:
                if chunk['type'] == 'text':
                    text_chunks.append(chunk)
                elif chunk['type'] == 'image':
                    image_chunks.append(chunk)
                elif chunk['type'] == 'mixed':
                    mixed_chunks.append(chunk)
            
            # Informer l'utilisateur du nombre de chunks par type
            print(f"\n[INFO] Processing chunks for course '{course_name}' (ID: {course_id})")
            print(f"[INFO] Found {len(text_chunks)} text chunks, {len(image_chunks)} image chunks, and {len(mixed_chunks)} mixed chunks")
            
            # Traiter les chunks textuels
            if text_chunks:
                print(f"[INFO] Processing text chunks...")
                
                # Extraire le contenu textuel
                text_contents = [chunk['content'] for chunk in text_chunks]
                
                # Générer les embeddings
                text_embeddings = await embeddings_client.encode_text(text_contents)
                
                # Stocker les chunks avec leurs embeddings
                total = len(text_chunks)
                for i, (chunk, embedding) in enumerate(zip(text_chunks, text_embeddings)):
                    # Afficher la progression tous les 10% ou pour le dernier item
                    if i % max(1, total // 10) == 0 or i == total - 1:
                        log_progress(i+1, total, prefix='Text Chunks:', suffix='Complete')
                    
                    vector_data = {
                        'course_id': course_id,
                        'chunk_index': i,
                        'chunk_text': chunk['content'],
                        'chunk_type': 'text',
                        'page_number': chunk['page_number'],
                        'embedding': embedding,
                        'metadata': metadata_utf8,
                        'is_multimodal': False
                    }
                    
                    # Insertion dans Supabase
                    self.supabase.table('vectors').insert(vector_data).execute()
            
            # Traiter les chunks d'images
            if image_chunks:
                print(f"[INFO] Processing image chunks...")
                
                # Extraire les données d'images
                image_data_list = [chunk['content'] for chunk in image_chunks]
                
                # Générer les embeddings d'images
                image_embeddings = await embeddings_client.encode_images(image_data_list)
                
                # Stocker les chunks avec leurs embeddings
                total = len(image_chunks)
                for i, (chunk, embedding) in enumerate(zip(image_chunks, image_embeddings)):
                    # Afficher la progression tous les 10% ou pour le dernier item
                    if i % max(1, total // 10) == 0 or i == total - 1:
                        log_progress(i+1, total, prefix='Image Chunks:', suffix='Complete')
                    
                    vector_data = {
                        'course_id': course_id,
                        'chunk_index': i + len(text_chunks),  # Continuer l'indexation
                        'chunk_text': '',  # Pas de texte pour les images
                        'chunk_type': 'image',
                        'page_number': chunk['page_number'],
                        'embedding': embedding,
                        'metadata': json.dumps(chunk['metadata'], ensure_ascii=False),
                        'image_data': chunk['content'],
                        'is_multimodal': False
                    }
                    
                    # Insertion dans Supabase
                    self.supabase.table('vectors').insert(vector_data).execute()
            
            # Traiter les chunks mixtes (texte + image)
            if mixed_chunks:
                print(f"[INFO] Processing {len(mixed_chunks)} mixed chunks...")
                
                # Extraire le contenu textuel
                mixed_texts = [chunk['content'] for chunk in mixed_chunks]
                
                # Générer les embeddings textuels
                mixed_text_embeddings = await embeddings_client.encode_text(mixed_texts)
                
                # Stocker les chunks avec leurs embeddings
                total = len(mixed_chunks)
                for i, (chunk, embedding) in enumerate(zip(mixed_chunks, mixed_text_embeddings)):
                    # Afficher la progression tous les 10% ou pour le dernier item
                    if i % max(1, total // 10) == 0 or i == total - 1:
                        log_progress(i+1, total, prefix='Mixed Chunks:', suffix='Complete')
                    
                    vector_data = {
                        'course_id': course_id,
                        'chunk_index': i + len(text_chunks) + len(image_chunks),  # Continuer l'indexation
                        'chunk_text': chunk['content'],
                        'chunk_type': 'mixed',
                        'page_number': chunk['page_number'],
                        'embedding': embedding,  # Utiliser l'embedding textuel
                        'metadata': json.dumps(chunk['metadata'], ensure_ascii=False),
                        'image_data': chunk['image_data'],
                        'is_multimodal': True
                    }
                    
                    # Insertion dans Supabase
                    self.supabase.table('vectors').insert(vector_data).execute()
            
            print(f"[INFO] Successfully stored all chunks for course '{course_name}'")
                    
        except Exception as e:
            logger.error(f"Failed to store chunks with embeddings: {str(e)}")
            raise

    # Garder également la méthode originale pour la compatibilité
    async def store_chunks(self, course_name: str, chunks: List[Dict[str, Any]]):
        try:
            course_id = await self.get_course_id(course_name)
            
            # Stocker les chunks avec un index
            total = len(chunks)
            print(f"[INFO] Storing {total} chunks for course '{course_name}'")
            
            for index, chunk in enumerate(chunks):
                # Afficher la progression tous les 5% ou pour le dernier item
                if index % max(1, total // 20) == 0 or index == total - 1:
                    log_progress(index+1, total, prefix='Storing Chunks:', suffix='Complete')
                
                vector_data = {
                    'course_id': course_id,
                    'chunk_index': index,
                    'chunk_text': chunk.get('content', ''),
                    'chunk_type': chunk['type'],
                    'page_number': chunk['page_number'],
                    'metadata': json.dumps(chunk['metadata'])
                }
                
                # Ajouter les données d'image si présentes
                if chunk['type'] == 'image':
                    vector_data['image_data'] = chunk['content']
                    vector_data['is_multimodal'] = False
                elif chunk['type'] == 'mixed':
                    vector_data['image_data'] = chunk.get('image_data', '')
                    vector_data['is_multimodal'] = True

                self.supabase.table('vectors').insert(vector_data).execute()
                    
        except Exception as e:
            logger.error(f"Failed to store chunks: {str(e)}")
            raise

    async def delete_vectors_by_course_id(self, course_id: int):
        """Supprime tous les vectors liés à un cours"""
        try:
            self.supabase.table('vectors')\
                .delete()\
                .eq('course_id', course_id)\
                .execute()
            logger.info(f"Deleted all vectors for course {course_id}")
        except Exception as e:
            logger.error(f"Failed to delete vectors for course {course_id}: {str(e)}")
            raise
    
    async def search_vectors(self, query_embedding, top_k=5):
        """
        Recherche des vectors par similarité avec l'embedding de requête
        """
        try:
            # Exécuter la requête
            result = self.supabase.rpc(
                'match_documents', 
                {
                    'query_embedding': query_embedding,
                    'match_count': top_k
                }
            ).execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} matches")
                return result.data
            else:
                logger.warning("No matching documents found")
                return []
            
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []