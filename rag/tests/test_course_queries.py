# tests/test_course_queries.py
import os
import sys
import logging
import json
from tabulate import tabulate  # Si tabulate est installé, sinon nous utiliserons un format simple

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.search.rag_engine import get_rag_engine

# Configuration du logging minimale
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def test_course_queries(course_id=None, verbose=False):
    """
    Teste le moteur de recherche avec des requêtes pertinentes au cours d'électronique.
    Affiche les résultats de manière lisible.
    
    Args:
        course_id (int, optional): ID du cours dans Supabase. Si None, cherche dans tous les cours.
        verbose (bool): Si True, affiche des détails supplémentaires.
    """
    # Initialiser le moteur RAG
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
    
    results = []
    
    # En-tête de table
    print("\n" + "="*80)
    print(f"TEST DES REQUÊTES POUR LE COURS ID: {course_id if course_id else 'TOUS'}")
    print("="*80)
    
    # Tester chaque requête
    for i, query in enumerate(electronic_queries, 1):
        print(f"\nRequête {i}/{len(electronic_queries)}: '{query}'")
        
        # Construire le contexte pour le LLM
        try:
            llm_context = rag_engine.build_context_for_llm(query, top_k=3)
            metadata = llm_context.get('metadata', {})
            pages_info = metadata.get('pages', [])
            
            # Filtrer les résultats pour ce cours spécifique
            if course_id:
                course_results = [p for p in pages_info if p.get('course_id') == course_id]
            else:
                course_results = pages_info
            
            if course_results:
                print(f"✅ {len(course_results)} résultats pertinents trouvés")
                
                # Afficher les résultats dans un format tabulaire
                table_data = []
                for j, result in enumerate(course_results[:3], 1):
                    page_num = result.get('page_number', 'N/A')
                    similarity = result.get('similarity', 0)
                    course_id = result.get('course_id', 'N/A')
                    table_data.append([j, page_num, f"{similarity:.4f}", course_id])
                
                # Afficher les résultats sous forme de tableau
                try:
                    print(tabulate(table_data, headers=['#', 'Page', 'Similarité', 'Cours ID'], tablefmt='grid'))
                except NameError:
                    for row in table_data:
                        print(f"  Résultat {row[0]}: Page {row[1]}, Similarité {row[2]}, Cours ID {row[3]}")
                
                # Stocker le résultat pour le résumé
                results.append({
                    "query": query,
                    "success": True,
                    "result_count": len(course_results),
                    "top_result": {
                        "page": course_results[0].get('page_number', 'N/A') if course_results else 'N/A',
                        "similarity": course_results[0].get('similarity', 0) if course_results else 0
                    }
                })
            else:
                print("❌ Aucun résultat pertinent trouvé")
                results.append({
                    "query": query,
                    "success": False,
                    "result_count": 0
                })
                
            # Si mode verbose, afficher le contexte généré
            if verbose and llm_context.get('context'):
                context_preview = llm_context['context'][:200] + "..." if len(llm_context['context']) > 200 else llm_context['context']
                print("\nAperçu du contexte généré:")
                print(context_preview)
                
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {str(e)}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Afficher un résumé des résultats
    success_count = sum(1 for r in results if r.get('success', False))
    print("\n" + "="*80)
    print(f"RÉSUMÉ: {success_count}/{len(electronic_queries)} requêtes ont donné des résultats")
    print("="*80)
    
    return results

if __name__ == "__main__":
    # Récupérer l'ID du cours depuis les arguments (optionnel)
    course_id = None
    verbose = False
    
    # Analyser les arguments
    for arg in sys.argv[1:]:
        if arg.startswith("--course="):
            try:
                course_id = int(arg.split("=")[1])
            except ValueError:
                print("L'ID du cours doit être un nombre entier.")
                sys.exit(1)
        elif arg == "--verbose" or arg == "-v":
            verbose = True
    
    # Exécuter les tests
    test_course_queries(course_id, verbose)