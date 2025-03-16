# src/api/optimizations.py
import logging
import time
import asyncio  # Ajout de l'import manquant
from functools import lru_cache, wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def rate_limiter(calls: int, period: float):
    """
    Décorateur pour limiter le taux d'appels à une fonction.
    
    Args:
        calls: Nombre maximal d'appels autorisés dans la période
        period: Période en secondes
    """
    def decorator(func):
        # Utiliser une variable non locale pour le suivi des appels
        calls_record = []
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Nettoyer les anciens appels
            current_time = time.time()
            while calls_record and current_time - calls_record[0] > period:
                calls_record.pop(0)
            
            # Vérifier si on a atteint la limite
            if len(calls_record) >= calls:
                wait_time = period - (current_time - calls_record[0])
                if wait_time > 0:
                    logger.warning(f"Rate limit atteint, attente de {wait_time:.2f} secondes")
                    time.sleep(wait_time)
            
            # Enregistrer l'appel et appeler la fonction
            calls_record.append(time.time())
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Nettoyer les anciens appels
            current_time = time.time()
            while calls_record and current_time - calls_record[0] > period:
                calls_record.pop(0)
            
            # Vérifier si on a atteint la limite
            if len(calls_record) >= calls:
                wait_time = period - (current_time - calls_record[0])
                if wait_time > 0:
                    logger.warning(f"Rate limit atteint, attente de {wait_time:.2f} secondes")
                    time.sleep(wait_time)
            
            # Enregistrer l'appel et appeler la fonction
            calls_record.append(time.time())
            return func(*args, **kwargs)
        
        # Retourner le bon wrapper selon que la fonction est asynchrone ou non
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

# Exemple de cache pour les résultats fréquents avec une durée de vie
def timed_lru_cache(seconds: int, maxsize: int = 128):
    """
    Décorateur pour mettre en cache les résultats d'une fonction avec durée de vie.
    
    Args:
        seconds: Durée de vie en secondes
        maxsize: Taille maximale du cache
    """
    def decorator(func):
        # Créer le cache
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Créer une clé de cache
            key = str(args) + str(kwargs)
            
            # Vérifier si le résultat est en cache et valide
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return result
            
            # Appeler la fonction et mettre en cache
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            
            # Nettoyer le cache si nécessaire
            if len(cache) > maxsize:
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                cache.pop(oldest_key)
                
            return result
        
        return wrapper
    
    return decorator