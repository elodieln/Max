# tests/test_search_optimizations.py
import os
import sys
import time
import logging

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search.search_optimizations import timing_decorator, cached_query_embedding, process_queries_in_batch
from src.embeddings.multimodal_embeddings import get_multimodal_embeddings_client
from src.search.rag_engine import get_rag_engine

# Configuration du logging - Réduire le niveau pour certains modules
logging.basicConfig(
    level=logging.WARNING,  # Niveau global à WARNING pour réduire le bruit
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configurer notre logger spécifique
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Spécifiquement INFO pour notre module

# Créer un handler pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

@timing_decorator
def test_search_performance():
    """
    Teste les optimisations de performance de recherche.
    """
    try:
        # Initialiser le client d'embeddings
        embeddings_client = get_multimodal_embeddings_client()
        print("Client d'embeddings initialisé")
        
        # Liste de requêtes pour les tests (réduite pour éviter les erreurs 500)
        test_queries = [
            "Qu'est-ce qu'un condensateur?",
            "Comment fonctionne un transistor?",
            "Expliquez les circuits RC"
        ]
        
        # Test de génération d'embeddings sans optimisations (une à la fois)
        print("\n=== Test sans optimisations ===")
        start_time = time.time()
        
        for i, query in enumerate(test_queries):
            print(f"[{i+1}/{len(test_queries)}] Génération d'embedding pour: '{query}'")
            try:
                _ = embeddings_client.encode_queries([query])  # Une seule requête à la fois
                # Pause pour éviter de surcharger l'API
                time.sleep(1)  
            except Exception as e:
                print(f"ERREUR: {str(e)}")
        
        standard_time = time.time() - start_time
        print(f"Temps total sans optimisations: {standard_time:.4f} secondes")
        
        # Test avec la mise en cache
        print("\n=== Test avec mise en cache ===")
        start_time = time.time()
        
        for i, query in enumerate(test_queries):
            print(f"[{i+1}/{len(test_queries)}] Génération d'embedding (avec cache) pour: '{query}'")
            try:
                _ = cached_query_embedding(query, lambda q: embeddings_client.encode_queries([q[0]]))
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
            except Exception as e:
                print(f"ERREUR: {str(e)}")
        
        cache_time = time.time() - start_time
        print(f"Temps total avec mise en cache: {cache_time:.4f} secondes")
        if standard_time > 0:
            print(f"Amélioration: {(1 - cache_time/standard_time)*100:.2f}%")
        
        # Test avec traitement par lots (de taille 1)
        print("\n=== Test avec traitement par lots (taille 1) ===")
        start_time = time.time()
        
        # Fonction de traitement par lots
        def process_batch(batch):
            print(f"Traitement d'un lot de {len(batch)} requêtes")
            results = []
            for i, query in enumerate(batch):
                print(f"  - Traitement de la requête {i+1}/{len(batch)}")
                try:
                    result = embeddings_client.encode_queries([query])
                    results.append(result[0] if result else None)
                    print("    ✓ Embedding généré avec succès")
                except Exception as e:
                    print(f"    ✗ Erreur: {str(e)}")
                    results.append(None)
                # Pause pour éviter de surcharger l'API
                time.sleep(1)
            return results
        
        _ = process_queries_in_batch(test_queries, batch_size=1, processor_func=process_batch)
        
        batch_time = time.time() - start_time
        print(f"Temps total avec traitement par lots: {batch_time:.4f} secondes")
        if standard_time > 0:
            print(f"Amélioration par rapport à standard: {(1 - batch_time/standard_time)*100:.2f}%")
        
        # Test de performance du moteur RAG complet avec une seule requête
        print("\n=== Test de performance du moteur RAG ===")
        rag_engine = get_rag_engine()
        
        @timing_decorator
        def search_with_rag(query):
            print(f"Recherche RAG pour: '{query}'")
            try:
                result = rag_engine.retrieve(query, top_k=3)
                num_results = len(result.get("results", []))
                print(f"Nombre de résultats: {num_results}")
                return result
            except Exception as e:
                print(f"ERREUR lors de la recherche RAG: {str(e)}")
                return {"query": query, "results": [], "context": {}}
        
        # Tester une requête avec le moteur RAG complet
        sample_query = "Qu'est-ce qu'un condensateur et comment fonctionne-t-il?"
        search_results = search_with_rag(sample_query)
        
        # Afficher un résumé des résultats
        result_count = len(search_results.get("results", []))
        if result_count > 0:
            print(f"\nDétails des résultats de recherche:")
            for i, result in enumerate(search_results.get("results", [])[:3]):
                similarity = result.get("similarity", 0)
                page_num = result.get("page_number", "N/A")
                print(f"  Résultat {i+1}: Page {page_num}, Similarité {similarity:.4f}")
        
        return {
            "standard_time": standard_time,
            "cache_time": cache_time,
            "batch_time": batch_time,
            "result_count": result_count
        }
        
    except Exception as e:
        print(f"ERREUR CRITIQUE: {str(e)}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("TESTS D'OPTIMISATION DE LA RECHERCHE")
    print("="*60)
    
    results = test_search_performance()
    
    if results:
        print("\n" + "="*60)
        print("RÉSUMÉ DES RÉSULTATS")
        print("="*60)
        print(f"Temps standard: {results['standard_time']:.2f}s")
        print(f"Temps avec cache: {results['cache_time']:.2f}s")
        print(f"Temps avec lots: {results['batch_time']:.2f}s")
        print(f"Nombre de résultats RAG: {results.get('result_count', 0)}")
    else:
        print("\nLes tests n'ont pas pu être complétés correctement.")