# tests/process_course_document.py
import os
import sys
import logging
import time
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processing.pdf_extractor import PDFExtractor
from src.embeddings.embedding_generator import get_embedding_generator
from src.storage.supabase_client import get_supabase_client

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('src.storage').setLevel(logging.WARNING)

def process_complete_document(pdf_path, course_id=None, course_name=None):
    """
    Traite un document PDF complet et génère des embeddings pour toutes les pages.
    
    Args:
        pdf_path (str): Chemin vers le fichier PDF
        course_id (int, optional): ID du cours dans Supabase. Si None, un nouveau cours sera créé.
        course_name (str, optional): Nom du cours. Obligatoire si course_id est None.
    
    Returns:
        dict: Résultat du traitement avec statistiques
    """
    try:
        # 1. Extraire toutes les pages du PDF
        logger.info(f"Extraction du PDF: {pdf_path}")
        pdf_extractor = PDFExtractor()
        
        # Si course_id est None, créer un nouveau cours
        if course_id is None:
            if course_name is None:
                course_name = Path(pdf_path).stem
                
            # Créer un nouveau cours dans Supabase
            supabase = get_supabase_client()
            result = supabase.table("courses").insert({
                "name": course_name,
                "pdf_url": pdf_path,
                "year": "ING2"  # Valeur par défaut, à adapter selon vos besoins
            }).execute()
            
            if result.data and len(result.data) > 0:
                course_id = result.data[0]["id"]
                logger.info(f"Nouveau cours créé avec ID: {course_id}")
            else:
                raise Exception("Échec de la création du cours dans Supabase")
        
        # Extraire les pages du PDF
        pages_info = pdf_extractor.extract_from_pdf(pdf_path, course_id)
        logger.info(f"Extraction terminée: {len(pages_info)} pages extraites")
        
        # Enregistrer les pages dans Supabase
        supabase = get_supabase_client()
        page_ids = pdf_extractor.save_pages_to_supabase(pages_info, supabase)
        logger.info(f"Pages enregistrées dans Supabase: {len(page_ids)}/{len(pages_info)}")
        
        # Mettre à jour les pages_info avec les IDs récupérés
        for i, page_id in enumerate(page_ids):
            if i < len(pages_info):
                pages_info[i]['id'] = page_id
        
        # 2. Générer des embeddings pour toutes les pages
        logger.info("Génération des embeddings pour toutes les pages...")
        embedding_generator = get_embedding_generator()
        
        # Filtrer pages_info pour inclure uniquement les pages avec un ID
        pages_with_ids = [page for page in pages_info if 'id' in page]
        
        # Traiter les pages une par une pour éviter les erreurs 500
        batch_size = 1  # Réduire à 1 page à la fois
        total_pages = len(pages_with_ids)
        successful_embeddings = []
        
        for i in range(0, total_pages, batch_size):
            end_idx = min(i + batch_size, total_pages)
            batch = pages_with_ids[i:end_idx]
            logger.info(f"Traitement du lot {i//batch_size + 1}/{(total_pages + batch_size - 1)//batch_size} (pages {i+1}-{end_idx})")
            
            # Essayer jusqu'à 3 fois en cas d'erreur
            retry_count = 0
            success = False
            
            while retry_count < 3 and not success:
                try:
                    # Générer et stocker les embeddings pour ce lot
                    successful_ids = embedding_generator.generate_and_store_embeddings(batch)
                    if successful_ids:
                        successful_embeddings.extend(successful_ids)
                        logger.info(f"Lot traité avec succès: {len(successful_ids)}/{len(batch)} embeddings générés")
                        success = True
                    else:
                        logger.warning(f"Aucun embedding généré pour ce lot, tentative {retry_count + 1}/3")
                        retry_count += 1
                        time.sleep(2)  # Attendre 2 secondes avant de réessayer
                except Exception as e:
                    logger.error(f"Erreur lors de la génération d'embeddings, tentative {retry_count + 1}/3: {str(e)}")
                    retry_count += 1
                    time.sleep(2)  # Attendre 2 secondes avant de réessayer
            
            # Pause plus longue entre les lots pour éviter de surcharger l'API
            time.sleep(1)
        
        # 3. Résumé des résultats
        result = {
            "course_id": course_id,
            "total_pages": total_pages,
            "successful_embeddings": len(successful_embeddings),
            "success_rate": len(successful_embeddings) / total_pages if total_pages > 0 else 0
        }
        
        logger.info(f"Traitement terminé avec un taux de réussite de {result['success_rate']*100:.2f}%")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document: {str(e)}")
        raise

def test_search_with_course_related_queries(course_id):
    """
    Teste le moteur de recherche avec des requêtes pertinentes au cours d'électronique.
    
    Args:
        course_id (int): ID du cours dans Supabase
    """
    try:
        # Importer le moteur RAG
        from src.search.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        
        # Questions pertinentes pour le cours d'électronique fondamentale
        electronic_queries = [
            "Qu'est-ce qu'un condensateur et comment fonctionne-t-il?",
            "Comment la convention récepteur fonctionne-t-elle?",
            "Quelle est la relation entre la résistance et la résistivité?",
            "Expliquez le modèle du condensateur réel",
            "Quels sont les différents types de condensateurs?",
            "Comment fonctionne un circuit intégré?",
            "Qu'est-ce que la loi d'Ohm et comment l'appliquer?",
            "Qu'est-ce que la vitesse de dérive des électrons?",
            "À quoi servent les condensateurs dans les applications de découplage?",
            "Comment les électrons se déplacent-ils dans un conducteur?"
        ]
        
        # Tester chaque requête
        for i, query in enumerate(electronic_queries):
            logger.info(f"\n=== Test de la requête {i+1}: '{query}' ===")
            
            # Construire le contexte pour le LLM
            llm_context = rag_engine.build_context_for_llm(query, top_k=3)
            
            # Afficher les métadonnées des résultats
            metadata = llm_context.get('metadata', {})
            pages_info = metadata.get('pages', [])
            
            logger.info(f"Nombre de résultats pertinents: {len(pages_info)}")
            
            # Filtrer les résultats pour ce cours spécifique
            course_results = [p for p in pages_info if p.get('course_id') == course_id]
            logger.info(f"Résultats pour ce cours: {len(course_results)}/{len(pages_info)}")
            
            # Afficher les meilleurs résultats
            for j, result in enumerate(course_results[:3]):
                logger.info(f"  Résultat {j+1}:")
                logger.info(f"    Page: {result.get('page_number')}")
                logger.info(f"    Similarité: {result.get('similarity', 0):.4f}")
                
    except Exception as e:
        logger.error(f"Erreur lors du test de recherche: {str(e)}")

if __name__ == "__main__":
    for handler in logging.root.handlers:
        handler.setLevel(logging.WARNING)
    # Réactiver l'affichage des logs pour notre module
    logging.getLogger(__name__).setLevel(logging.INFO)
    # Lire les arguments de la ligne de commande
    if len(sys.argv) < 2:
        print("Usage: python process_course_document.py <chemin_pdf> [<course_id>]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    course_id = None
    
    if len(sys.argv) > 2:
        try:
            course_id = int(sys.argv[2])
        except ValueError:
            print("L'ID du cours doit être un nombre entier.")
            sys.exit(1)
    
    # Traiter le document
    result = process_complete_document(pdf_path, course_id)
    
    # Si le traitement a réussi, tester le moteur de recherche
    if result.get("success_rate", 0) > 0:
        print("\nTest du moteur de recherche avec des requêtes pertinentes...")
        test_search_with_course_related_queries(result["course_id"])