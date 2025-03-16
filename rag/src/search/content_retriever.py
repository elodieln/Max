# src/search/content_retriever.py
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from src.storage.supabase_client import get_supabase_client
from PIL import Image

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentRetriever:
    """
    Service pour récupérer le contenu original des pages et des cours.
    """
    
    def __init__(self):
        """
        Initialise le récupérateur de contenu.
        """
        self.supabase = get_supabase_client()
        logger.info("Récupérateur de contenu initialisé")
    
    def get_page_content(self, page_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère le contenu complet d'une page.
        
        Args:
            page_id (int): ID de la page.
            
        Returns:
            Optional[Dict[str, Any]]: Contenu complet de la page ou None si non trouvée.
        """
        try:
            # Récupérer les informations de la page
            page_result = self.supabase.from_("pages").select(
                "id, page_number, image_path, content_text, course_id"
            ).eq("id", page_id).execute()
            
            if not page_result.data or len(page_result.data) == 0:
                logger.warning(f"Page non trouvée avec l'ID: {page_id}")
                return None
            
            page_info = page_result.data[0]
            
            # Récupérer les informations du cours
            course_id = page_info.get('course_id')
            if course_id:
                course_info = self.get_course_info(course_id)
                if course_info:
                    page_info['course'] = course_info
            
            # Vérifier si l'image existe
            image_path = page_info.get('image_path')
            if image_path and os.path.exists(image_path):
                page_info['image_exists'] = True
            else:
                page_info['image_exists'] = False
                logger.warning(f"L'image de la page {page_id} n'existe pas: {image_path}")
            
            return page_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contenu de la page {page_id}: {str(e)}")
            return None
    
    def get_course_info(self, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un cours.
        
        Args:
            course_id (int): ID du cours.
            
        Returns:
            Optional[Dict[str, Any]]: Informations du cours ou None si non trouvé.
        """
        try:
            # Récupérer les informations du cours
            course_result = self.supabase.from_("courses").select(
                "id, name, pdf_url, photo_url, year"
            ).eq("id", course_id).execute()
            
            if course_result.data and len(course_result.data) > 0:
                return course_result.data[0]
            else:
                logger.warning(f"Cours non trouvé avec l'ID: {course_id}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations du cours {course_id}: {str(e)}")
            return None
    
    def get_course_pages(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Récupère toutes les pages d'un cours.
        
        Args:
            course_id (int): ID du cours.
            
        Returns:
            List[Dict[str, Any]]: Liste des pages du cours.
        """
        try:
            # Récupérer les pages du cours
            pages_result = self.supabase.from_("pages").select(
                "id, page_number, image_path, content_text"
            ).eq("course_id", course_id).order("page_number").execute()
            
            if pages_result.data:
                logger.info(f"Récupération de {len(pages_result.data)} pages pour le cours {course_id}")
                return pages_result.data
            else:
                logger.warning(f"Aucune page trouvée pour le cours {course_id}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des pages du cours {course_id}: {str(e)}")
            return []
    
    def get_context_pages(self, page_id: int, context_size: int = 1) -> List[Dict[str, Any]]:
        """
        Récupère les pages environnantes pour fournir un contexte.
        
        Args:
            page_id (int): ID de la page centrale.
            context_size (int): Nombre de pages à récupérer avant et après.
            
        Returns:
            List[Dict[str, Any]]: Liste des pages de contexte.
        """
        try:
            # Récupérer d'abord la page pour obtenir course_id et page_number
            page_result = self.supabase.from_("pages").select(
                "id, page_number, course_id"
            ).eq("id", page_id).execute()
            
            if not page_result.data or len(page_result.data) == 0:
                logger.warning(f"Page non trouvée avec l'ID: {page_id}")
                return []
            
            page_info = page_result.data[0]
            course_id = page_info.get('course_id')
            page_number = page_info.get('page_number')
            
            if not course_id or not page_number:
                logger.warning(f"Informations incomplètes pour la page {page_id}")
                return []
            
            # Calculer les plages de pages à récupérer
            min_page = max(1, page_number - context_size)
            max_page = page_number + context_size
            
            # Récupérer les pages de contexte
            context_result = self.supabase.from_("pages").select(
                "id, page_number, image_path, content_text"
            ).eq("course_id", course_id).gte("page_number", min_page).lte("page_number", max_page).order("page_number").execute()
            
            if context_result.data:
                logger.info(f"Récupération de {len(context_result.data)} pages de contexte pour la page {page_id}")
                return context_result.data
            else:
                logger.warning(f"Aucune page de contexte trouvée pour la page {page_id}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des pages de contexte pour la page {page_id}: {str(e)}")
            return []

# Fonction pour obtenir une instance du récupérateur de contenu
def get_content_retriever() -> ContentRetriever:
    return ContentRetriever()