# src/utils/image_utils.py
import os
from PIL import Image
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def resize_image(image_path, max_width=600, max_height=600):  # Dimensions réduites
    """
    Redimensionne une image tout en conservant son ratio.
    
    Args:
        image_path (str): Chemin vers l'image à redimensionner.
        max_width (int): Largeur maximale.
        max_height (int): Hauteur maximale.
        
    Returns:
        str: Chemin vers l'image redimensionnée.
    """
    try:
        # Ouvrir l'image
        img = Image.open(image_path)
        
        # Obtenir les dimensions
        width, height = img.size
        
        # Vérifier si un redimensionnement est nécessaire
        if width <= max_width and height <= max_height:
            logger.info(f"L'image {image_path} ne nécessite pas de redimensionnement.")
            return image_path
            
        # Calculer le ratio
        ratio = min(max_width / width, max_height / height)
        
        # Calculer les nouvelles dimensions
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Redimensionner l'image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Créer le chemin pour l'image redimensionnée
        dir_name, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        resized_path = os.path.join(dir_name, f"{name}_resized{ext}")
        
        # Enregistrer l'image redimensionnée
        resized_img.save(resized_path)
        logger.info(f"Image redimensionnée enregistrée sous: {resized_path}")
        
        return resized_path
        
    except Exception as e:
        logger.error(f"Erreur lors du redimensionnement de l'image {image_path}: {str(e)}")
        return image_path

def optimize_image_for_embeddings(image_path):
    """
    Optimise une image pour la génération d'embeddings.
    
    Args:
        image_path (str): Chemin vers l'image à optimiser.
        
    Returns:
        str: Chemin vers l'image optimisée.
    """
    try:
        # D'abord redimensionner l'image
        resized_path = resize_image(image_path)
        
        # Ouvrir l'image redimensionnée
        img = Image.open(resized_path)
        
        # Créer le chemin pour l'image optimisée
        dir_name, file_name = os.path.split(resized_path)
        name, ext = os.path.splitext(file_name)
        optimized_path = os.path.join(dir_name, f"{name}_optimized{ext}")
        
        # Conversion en RGB si nécessaire (pour les images RGBA par exemple)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Optimiser et enregistrer l'image avec une qualité réduite
        img.save(optimized_path, optimize=True, quality=75)  # Qualité réduite à 75% au lieu de 85%
        logger.info(f"Image optimisée enregistrée sous: {optimized_path}")
        
        return optimized_path
        
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation de l'image {image_path}: {str(e)}")
        return image_path