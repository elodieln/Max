# src/processing/pdf_extractor.py
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Classe pour extraire du contenu (texte et images) à partir de fichiers PDF.
    """
    
    def __init__(self, images_dir="data/images"):
        """
        Initialise l'extracteur PDF.
        
        Args:
            images_dir (str): Répertoire où les images extraites seront stockées.
        """
        self.images_dir = images_dir
        # S'assurer que le répertoire d'images existe
        os.makedirs(self.images_dir, exist_ok=True)
        
    def extract_from_pdf(self, pdf_path, course_id=None):
        """
        Extrait le contenu (texte et images) de chaque page d'un fichier PDF.
        
        Args:
            pdf_path (str): Chemin vers le fichier PDF.
            course_id (int, optional): ID du cours auquel appartient le PDF.
            
        Returns:
            list: Liste de dictionnaires contenant les informations de chaque page.
                Chaque dictionnaire contient:
                - page_number (int): Numéro de la page
                - content_text (str): Texte extrait de la page
                - image_path (str): Chemin vers l'image générée pour cette page
        """
        if not os.path.exists(pdf_path):
            logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
            return []
            
        try:
            # Ouvrir le document PDF
            doc = fitz.open(pdf_path)
            
            # Créer un répertoire spécifique pour ce PDF
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            if course_id:
                pdf_dir = os.path.join(self.images_dir, f"course_{course_id}")
            else:
                pdf_dir = os.path.join(self.images_dir, pdf_name)
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Extraire le contenu de chaque page
            pages_info = []
            
            for page_number, page in enumerate(doc):
                # Extraire le texte
                text = page.get_text()
                
                # Convertir la page en image
                # Augmenter la résolution pour une meilleure qualité d'image
                zoom_factor = 2.0  # Facteur de zoom pour améliorer la qualité
                mat = fitz.Matrix(zoom_factor, zoom_factor)
                pix = page.get_pixmap(matrix=mat)
                
                # Créer un objet d'image PIL à partir du pixmap
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Enregistrer l'image
                image_filename = f"page_{page_number + 1}.png"
                image_path = os.path.join(pdf_dir, image_filename)
                img.save(image_path, "PNG")
                
                # Collecter les informations de la page
                page_info = {
                    "page_number": page_number + 1,
                    "content_text": text,
                    "image_path": image_path
                }
                
                if course_id:
                    page_info["course_id"] = course_id
                
                pages_info.append(page_info)
                
                logger.info(f"Page {page_number + 1}/{len(doc)} extraite avec succès")
                
            doc.close()
            return pages_info
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du PDF {pdf_path}: {str(e)}")
            return []
    
    def save_pages_to_supabase(self, pages_info, supabase):
        """
        Enregistre les informations des pages dans la base de données Supabase.
        
        Args:
            pages_info (list): Liste des informations de pages extraites.
            supabase: Client Supabase.
            
        Returns:
            list: Liste des IDs des pages insérées.
        """
        try:
            page_ids = []
            
            for page_info in pages_info:
                # Insertion dans la table 'pages'
                result = supabase.table('pages').insert(page_info).execute()
                
                # Récupérer l'ID de la page insérée
                if result.data and len(result.data) > 0:
                    page_id = result.data[0]['id']
                    page_ids.append(page_id)
                    logger.info(f"Page {page_info['page_number']} enregistrée avec l'ID {page_id}")
                else:
                    logger.warning(f"Impossible de récupérer l'ID pour la page {page_info['page_number']}")
            
            return page_ids
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des pages dans Supabase: {str(e)}")
            return []