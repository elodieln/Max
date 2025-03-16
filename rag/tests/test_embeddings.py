# tests/test_embeddings.py
import os
import sys
import logging
from dotenv import load_dotenv

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.supabase_client import get_supabase_client
from src.processing.pdf_extractor import PDFExtractor
from src.embeddings.embedding_generator import get_embedding_generator
from src.embeddings.multimodal_embeddings import get_multimodal_embeddings_client

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def test_query_embeddings():
    """
    Teste la génération d'embeddings pour les requêtes textuelles.
    """
    logger.info("Test de génération d'embeddings pour les requêtes textuelles...")
    
    # Créer une instance du client d'embeddings multimodal
    embeddings_client = get_multimodal_embeddings_client()
    
    # Tester avec une requête simple
    query = "Qu'est-ce qu'un condensateur ?"
    
    try:
        embeddings = embeddings_client.encode_queries([query])
        
        if embeddings and len(embeddings) > 0:
            embedding = embeddings[0]
            logger.info(f"Embedding généré avec succès pour la requête: {query}")
            logger.info(f"Dimension de l'embedding: {len(embedding)}")
            logger.info(f"Premiers éléments de l'embedding: {embedding[:5]}...")
            return True
        else:
            logger.error(f"Aucun embedding généré pour la requête: {query}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'embedding pour la requête: {str(e)}")
        return False

def test_document_embeddings(pdf_path=None):
    """
    Teste la génération d'embeddings pour les images extraites d'un PDF.
    
    Args:
        pdf_path (str, optional): Chemin vers le fichier PDF à utiliser pour le test.
            Si None, l'utilisateur sera invité à entrer un chemin.
    """
    if pdf_path is None:
        pdf_path = input("Entrez le chemin vers un fichier PDF pour le test: ")
    
    if not os.path.exists(pdf_path):
        logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
        return False
    
    logger.info(f"Test de génération d'embeddings pour les images extraites du PDF: {pdf_path}")
    
    # Créer une instance de l'extracteur PDF
    pdf_extractor = PDFExtractor()
    
    # Extraire les pages du PDF
    pages_info = pdf_extractor.extract_from_pdf(pdf_path)
    
    if not pages_info:
        logger.error(f"Aucune page extraite du PDF: {pdf_path}")
        return False
    
    logger.info(f"{len(pages_info)} pages extraites du PDF")
    
    # Prendre seulement la première page pour le test
    test_page = pages_info[0]
    
    # Créer une instance du client d'embeddings multimodal
    embeddings_client = get_multimodal_embeddings_client()
    
    try:
        # Générer l'embedding pour l'image de la page
        logger.info(f"Génération de l'embedding pour l'image: {test_page['image_path']}")
        embeddings = embeddings_client.encode_documents([test_page['image_path']])
        
        if embeddings and len(embeddings) > 0:
            embedding = embeddings[0]
            logger.info(f"Embedding généré avec succès pour l'image")
            logger.info(f"Dimension de l'embedding: {len(embedding)}")
            logger.info(f"Premiers éléments de l'embedding: {embedding[:5]}...")
            return True
        else:
            logger.error(f"Aucun embedding généré pour l'image")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'embedding pour l'image: {str(e)}")
        return False

def test_full_embedding_process(pdf_path=None, course_id=None):
    """
    Teste le processus complet de génération et stockage d'embeddings pour un PDF.
    
    Args:
        pdf_path (str, optional): Chemin vers le fichier PDF à utiliser pour le test.
            Si None, l'utilisateur sera invité à entrer un chemin.
        course_id (int, optional): ID du cours auquel appartient le PDF.
            Si None, l'utilisateur sera invité à entrer un ID.
    """
    if pdf_path is None:
        pdf_path = input("Entrez le chemin vers un fichier PDF pour le test: ")
    
    if not os.path.exists(pdf_path):
        logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
        return False
    
    if course_id is None:
        course_id_str = input("Entrez l'ID du cours (ou appuyez sur Entrée pour ignorer): ")
        course_id = int(course_id_str) if course_id_str.strip() else None
    
    logger.info(f"Test du processus complet pour le PDF: {pdf_path}")
    
    # Créer une instance de l'extracteur PDF
    pdf_extractor = PDFExtractor()
    
    # Extraire les pages du PDF
    pages_info = pdf_extractor.extract_from_pdf(pdf_path, course_id)
    
    if not pages_info:
        logger.error(f"Aucune page extraite du PDF: {pdf_path}")
        return False
    
    logger.info(f"{len(pages_info)} pages extraites du PDF")
    
    # Créer une instance du client Supabase
    supabase = get_supabase_client()
    
    # Enregistrer les pages dans Supabase
    page_ids = pdf_extractor.save_pages_to_supabase(pages_info, supabase)
    
    if not page_ids:
        logger.error("Aucune page enregistrée dans Supabase")
        return False
    
    logger.info(f"{len(page_ids)} pages enregistrées dans Supabase")
    
    # Récupérer les informations des pages depuis Supabase
    pages_from_db = []
    for page_id in page_ids:
        result = supabase.table("pages").select("id, image_path").eq("id", page_id).execute()
        if result.data and len(result.data) > 0:
            pages_from_db.append(result.data[0])
    
    if not pages_from_db:
        logger.error("Impossible de récupérer les informations des pages depuis Supabase")
        return False
    
    # Limiter à 2 pages pour le test
    test_pages = pages_from_db[:2]
    
    # Créer une instance du générateur d'embeddings
    embedding_generator = get_embedding_generator()
    
    # Générer et stocker les embeddings
    logger.info(f"Génération et stockage des embeddings pour {len(test_pages)} pages")
    successful_ids = embedding_generator.generate_and_store_embeddings(test_pages)
    
    if not successful_ids:
        logger.error("Aucun embedding généré et stocké avec succès")
        return False
    
    logger.info(f"{len(successful_ids)} embeddings générés et stockés avec succès")
    
    # Tester la recherche de similarité
    test_query = "Qu'est-ce qu'un condensateur ?"
    logger.info(f"Test de recherche de similarité avec la requête: {test_query}")
    
    # Générer l'embedding pour la requête
    query_embedding = embedding_generator.generate_query_embedding(test_query)
    
    if query_embedding is None:
        logger.error("Impossible de générer l'embedding pour la requête")
        return False
    
    # Rechercher les pages similaires
    storage = embedding_generator.storage
    similar_pages = storage.find_similar_pages(query_embedding)
    
    if not similar_pages:
        logger.warning("Aucune page similaire trouvée")
    else:
        logger.info(f"{len(similar_pages)} pages similaires trouvées")
        for i, page in enumerate(similar_pages):
            logger.info(f"Résultat {i+1}: Page ID {page['page_id']}, Similarité: {page['similarity']:.4f}")
    
    return True

if __name__ == "__main__":
    print("Tests du système d'embeddings")
    print("1. Tester la génération d'embeddings pour les requêtes textuelles")
    print("2. Tester la génération d'embeddings pour les images")
    print("3. Tester le processus complet de génération et stockage d'embeddings")
    
    choice = input("Entrez votre choix (1-3): ")
    
    if choice == "1":
        test_query_embeddings()
    elif choice == "2":
        test_document_embeddings()
    elif choice == "3":
        test_full_embedding_process()
    else:
        print("Choix invalide")