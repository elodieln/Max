# src/search/rag_engine.py
import logging
from typing import List, Dict, Any, Optional, Tuple
from src.search.search_service import get_search_service
from src.search.content_retriever import get_content_retriever

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Moteur de RAG (Retrieval-Augmented Generation) qui combine recherche et 
    récupération de contenu pour générer des réponses pertinentes.
    """
    
    def __init__(self):
        """
        Initialise le moteur RAG.
        """
        self.search_service = get_search_service()
        self.content_retriever = get_content_retriever()
        logger.info("Moteur RAG initialisé")
    
    def retrieve(self, query: str, top_k: int = 5, include_context: bool = True, context_size: int = 1) -> Dict[str, Any]:
        """
        Récupère les informations pertinentes en fonction d'une requête.
        
        Args:
            query (str): Requête textuelle.
            top_k (int): Nombre maximum de résultats à retourner.
            include_context (bool): Si True, inclut les pages de contexte.
            context_size (int): Nombre de pages de contexte à inclure.
            
        Returns:
            Dict[str, Any]: Résultats structurés avec les informations pertinentes.
        """
        try:
            # Rechercher les pages pertinentes
            search_results = self.search_service.search(query, top_k=top_k)
            
            if not search_results:
                logger.warning(f"Aucun résultat trouvé pour la requête: {query}")
                return {"query": query, "results": [], "context": {}}
            
            # Enrichir les résultats avec le contenu complet
            enriched_results = []
            context_pages = {}
            
            for result in search_results:
                page_id = result.get('id')
                if not page_id:
                    continue
                
                # Récupérer le contenu complet de la page
                page_content = self.content_retriever.get_page_content(page_id)
                if page_content:
                    # Fusionner les informations
                    result.update(page_content)
                    enriched_results.append(result)
                
                # Récupérer les pages de contexte si demandé
                if include_context:
                    context = self.content_retriever.get_context_pages(page_id, context_size)
                    if context:
                        context_pages[page_id] = context
            
            return {
                "query": query,
                "results": enriched_results,
                "context": context_pages
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations: {str(e)}")
            return {"query": query, "results": [], "context": {}, "error": str(e)}
    
    def build_context_for_llm(self, query: str, top_k: int = 3, context_size: int = 1) -> Dict[str, Any]:
        """
        Construit un contexte structuré et formaté pour le LLM.
        
        Args:
            query (str): Requête textuelle.
            top_k (int): Nombre maximum de résultats à inclure.
            context_size (int): Nombre de pages de contexte à inclure.
            
        Returns:
            Dict[str, Any]: Contexte structuré pour le LLM et métadonnées.
        """
        try:
            # Récupérer les informations pertinentes
            retrieval_results = self.retrieve(query, top_k, True, context_size)
            results = retrieval_results.get('results', [])
            context_pages = retrieval_results.get('context', {})
            
            if not results:
                logger.warning(f"Aucun résultat disponible pour construire le contexte LLM")
                return {"context": "", "metadata": {"success": False, "message": "Aucun contenu pertinent trouvé."}}
            
            # Construire le contexte formaté pour le LLM
            context_blocks = []
            metadata = {
                "success": True,
                "pages": [],
                "courses": {}
            }
            
            for result in results:
                page_id = result.get('id')
                page_number = result.get('page_number')
                course = result.get('courses', {})
                course_id = course.get('id') if course else None
                course_name = course.get('name', "Inconnu") if course else "Inconnu"
                content_text = result.get('content_text', "")
                similarity = result.get('similarity', 0)
                
                # Ajouter les métadonnées
                if course_id and course_id not in metadata["courses"]:
                    metadata["courses"][course_id] = {
                        "name": course_name,
                        "year": course.get('year', "") if course else ""
                    }
                
                metadata["pages"].append({
                    "id": page_id,
                    "page_number": page_number,
                    "course_id": course_id,
                    "similarity": similarity
                })
                
                # Construire le bloc de contexte
                context_block = f"--- Cours: {course_name} | Page: {page_number} ---\n{content_text}\n"
                context_blocks.append((context_block, similarity))
                
                # Ajouter le contexte des pages environnantes si disponible
                if page_id in context_pages:
                    for ctx_page in context_pages[page_id]:
                        ctx_id = ctx_page.get('id')
                        if ctx_id == page_id:  # Éviter les doublons
                            continue
                        
                        ctx_number = ctx_page.get('page_number')
                        ctx_text = ctx_page.get('content_text', "")
                        
                        # Ajouter avec une similarité légèrement inférieure
                        ctx_similarity = similarity * 0.8  # Réduire l'importance
                        ctx_block = f"--- Cours: {course_name} | Page: {ctx_number} (Contexte) ---\n{ctx_text}\n"
                        context_blocks.append((ctx_block, ctx_similarity))
                        
                        # Ajouter aux métadonnées
                        metadata["pages"].append({
                            "id": ctx_id,
                            "page_number": ctx_number,
                            "course_id": course_id,
                            "similarity": ctx_similarity,
                            "is_context": True
                        })
            
            # Trier les blocs par similarité et construire le contexte final
            context_blocks.sort(key=lambda x: x[1], reverse=True)
            full_context = "\n".join([block for block, _ in context_blocks])
            
            return {
                "context": full_context,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la construction du contexte pour le LLM: {str(e)}")
            return {"context": "", "metadata": {"success": False, "message": str(e)}}

# Fonction pour obtenir une instance du moteur RAG
def get_rag_engine() -> RAGEngine:
    return RAGEngine()