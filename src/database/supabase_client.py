# src/database/supabase_client.py
import os
from supabase import create_client
import logging
from typing import List, Dict, Any
import json

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

    async def store_chunks(self, course_name: str, chunks: List[Dict[str, Any]]):
        try:
            course_id = await self.get_course_id(course_name)
            
            # Stocker les chunks avec un index
            for index, chunk in enumerate(chunks):
                vector_data = {
                    'course_id': course_id,
                    'chunk_index': index,  # Ajout de l'index
                    'chunk_text': chunk['content'],
                    'chunk_type': chunk['type'],
                    'page_number': chunk['page_number'],
                    'metadata': json.dumps(chunk['metadata'])
                }

                self.supabase.table('vectors').insert(vector_data).execute()
                logger.info(f"Stored {chunk['type']} chunk {index} for page {chunk['page_number']}")
                    
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