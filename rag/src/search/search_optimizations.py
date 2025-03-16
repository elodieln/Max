# src/search/search_optimizations.py
import logging
import time
from functools import lru_cache
from typing import List, Dict, Any, Tuple, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Décorateur pour mesurer le temps d'exécution
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Fonction {func.__name__} exécutée en {end_time - start_time:.4f} secondes")
        return result
    return wrapper

# Mise en cache des embeddings de requêtes fréquentes
@lru_cache(maxsize=100)
def cached_query_embedding(query: str, client_func) -> Optional[List[float]]:
    """
    Utilise un cache pour éviter de recalculer les embeddings de requêtes déjà vues.
    
    Args:
        query (str): Requête textuelle.
        client_func: Fonction client pour générer l'embedding.
        
    Returns:
        Optional[List[float]]: Embedding ou None si erreur.
    """
    try:
        # Nettoyer la requête (normalisation)
        normalized_query = query.strip().lower()
        
        # Vérifier si la requête est vide
        if not normalized_query:
            return None
            
        # Générer l'embedding
        embeddings = client_func([normalized_query])
        
        if embeddings and len(embeddings) > 0:
            return embeddings[0]
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'embedding mis en cache: {str(e)}")
        return None

# Optimisation pour regrouper les requêtes similaires
def group_similar_queries(queries: List[str], threshold: float = 0.95) -> List[List[int]]:
    """
    Regroupe les requêtes similaires pour réduire le nombre d'appels d'embedding.
    Cette fonction est un placeholder pour une implémentation plus sophistiquée.
    
    Args:
        queries (List[str]): Liste de requêtes.
        threshold (float): Seuil de similarité.
        
    Returns:
        List[List[int]]: Groupes d'indices de requêtes similaires.
    """
    # Cette fonction est un placeholder pour une implémentation plus sophistiquée
    # En pratique, nous pourrions utiliser une similarité de texte ou d'embedding
    # Pour l'instant, chaque requête est dans son propre groupe
    return [[i] for i in range(len(queries))]

# Batch processing pour les requêtes multiples
def process_queries_in_batch(queries: List[str], batch_size: int = 10, processor_func=None) -> List[Any]:
    """
    Traite plusieurs requêtes par lots pour améliorer les performances.
    
    Args:
        queries (List[str]): Liste de requêtes.
        batch_size (int): Taille de chaque lot.
        processor_func: Fonction de traitement à appliquer à chaque lot.
        
    Returns:
        List[Any]: Résultats pour toutes les requêtes.
    """
    if not processor_func:
        logger.error("Aucune fonction de traitement fournie")
        return []
        
    results = []
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i + batch_size]
        logger.info(f"Traitement du lot {i//batch_size + 1}/{(len(queries) + batch_size - 1)//batch_size}")
        
        batch_results = processor_func(batch)
        results.extend(batch_results)
        
        # Petite pause pour ne pas surcharger l'API
        if i + batch_size < len(queries):
            time.sleep(0.5)
    
    return results