# tests/test_rag_engine.py
import os
import sys
import json
import logging
from typing import Dict, Any

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search.rag_engine import get_rag_engine

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rag_engine(query: str, top_k: int = 3):
    """
    Teste le moteur RAG avec une requête spécifique.
    
    Args:
        query (str): Requête à tester.
        top_k (int): Nombre de résultats à retourner.
    """
    try:
        # Initialiser le moteur RAG
        rag_engine = get_rag_engine()
        logger.info(f"Moteur RAG initialisé")
        
        # Tester la recherche de base
        logger.info(f"Test de recherche avec la requête: '{query}'")
        search_results = rag_engine.retrieve(query, top_k=top_k)
        
        # Afficher les résultats
        logger.info(f"Nombre de résultats: {len(search_results['results'])}")
        for i, result in enumerate(search_results['results']):
            logger.info(f"Résultat {i+1}:")
            logger.info(f"  Page ID: {result.get('id')}")
            logger.info(f"  Page numéro: {result.get('page_number')}")
            logger.info(f"  Similarité: {result.get('similarity', 0):.4f}")
            
            course = result.get('courses', {})
            course_name = course.get('name', "Inconnu") if course else "Inconnu"
            logger.info(f"  Cours: {course_name}")
            
            # Afficher un extrait du texte
            content_text = result.get('content_text', "")
            preview = content_text[:100] + "..." if len(content_text) > 100 else content_text
            logger.info(f"  Extrait: {preview}")
            logger.info("---")
        
        # Tester la génération de contexte pour le LLM
        logger.info(f"Test de génération de contexte pour le LLM")
        llm_context = rag_engine.build_context_for_llm(query, top_k=top_k)
        
        # Afficher les métadonnées
        metadata = llm_context.get('metadata', {})
        logger.info(f"Métadonnées: {json.dumps(metadata, indent=2)}")
        
        # Afficher un aperçu du contexte
        context = llm_context.get('context', "")
        context_preview = context[:200] + "..." if len(context) > 200 else context
        logger.info(f"Aperçu du contexte: {context_preview}")
        
        return {
            "search_results": search_results,
            "llm_context": llm_context
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test du moteur RAG: {str(e)}")
        return None

if __name__ == "__main__":
    # Si des arguments sont fournis, utiliser le premier comme requête
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = "Qu'est-ce qu'un condensateur et comment fonctionne-t-il?"
    
    # Définir le nombre de résultats à retourner
    top_k = 3
    if len(sys.argv) > 2:
        try:
            top_k = int(sys.argv[2])
        except:
            pass
    
    # Exécuter le test
    test_rag_engine(query, top_k)