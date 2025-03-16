# tests/test_pdf_extractor.py
import os
import sys
import logging
from dotenv import load_dotenv

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing.pdf_extractor import PDFExtractor
from src.storage.supabase_client import get_supabase_client

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_extraction(pdf_path, save_to_supabase=False):
    """
    Teste l'extraction de contenu à partir d'un fichier PDF.
    
    Args:
        pdf_path (str): Chemin vers le fichier PDF à tester.
        save_to_supabase (bool): Si True, enregistre les pages extraites dans Supabase.
    """
    try:
        logger.info(f"Test d'extraction du PDF: {pdf_path}")
        
        # Créer l'extracteur PDF
        extractor = PDFExtractor()
        
        # Extraire le contenu du PDF
        pages_info = extractor.extract_from_pdf(pdf_path)
        
        # Afficher les résultats
        logger.info(f"Nombre de pages extraites: {len(pages_info)}")
        
        for i, page_info in enumerate(pages_info[:2]):  # Afficher les 2 premières pages
            logger.info(f"Page {page_info['page_number']}:")
            logger.info(f"  Chemin de l'image: {page_info['image_path']}")
            # Afficher les 100 premiers caractères du texte
            text_preview = page_info['content_text'][:100].replace('\n', ' ')
            logger.info(f"  Aperçu du texte: {text_preview}...")
        
        if len(pages_info) > 2:
            logger.info("... et plus de pages")
        
        # Si demandé, enregistrer dans Supabase
        if save_to_supabase and pages_info:
            logger.info("Enregistrement des pages dans Supabase...")
            
            # Obtenir le client Supabase
            supabase = get_supabase_client()
            
            # Pour un test, on ajoute un course_id artificiel
            # Dans un cas réel, ce serait l'ID d'un cours existant
            test_course_id = None
            
            # Vérifier si le cours existe déjà ou en créer un pour le test
            course_name = os.path.basename(pdf_path).split('.')[0]
            courses = supabase.table('courses').select('*').eq('name', course_name).execute()
            
            if courses.data and len(courses.data) > 0:
                test_course_id = courses.data[0]['id']
                logger.info(f"Cours trouvé avec l'ID: {test_course_id}")
            else:
                # Créer un cours de test si nécessaire
                new_course = {
                    'name': course_name,
                    'pdf_url': pdf_path,
                    'year': 'ING1'  # Valeur par défaut pour le test
                }
                result = supabase.table('courses').insert(new_course).execute()
                if result.data and len(result.data) > 0:
                    test_course_id = result.data[0]['id']
                    logger.info(f"Nouveau cours créé avec l'ID: {test_course_id}")
            
            # Ajouter le course_id à chaque page
            for page in pages_info:
                page['course_id'] = test_course_id
            
            # Enregistrer les pages
            page_ids = extractor.save_pages_to_supabase(pages_info, supabase)
            logger.info(f"Pages enregistrées avec les IDs: {page_ids}")
        
        return pages_info
        
    except Exception as e:
        logger.error(f"Erreur lors du test d'extraction: {str(e)}")
        return []

if __name__ == "__main__":
    # Vérifier si un chemin de PDF a été fourni en argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        save_to_db = len(sys.argv) > 2 and sys.argv[2].lower() == 'save'
        test_pdf_extraction(pdf_path, save_to_db)
    else:
        logger.error("Veuillez fournir le chemin vers un fichier PDF à tester.")
        logger.info("Usage: python test_pdf_extractor.py <chemin_pdf> [save]")
        logger.info("  Ajoutez 'save' comme second argument pour enregistrer dans Supabase.")