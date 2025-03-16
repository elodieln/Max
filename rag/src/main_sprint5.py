"""
Application principale pour le Sprint 5 - Génération de réponses éducatives
Ce script intègre tous les composants développés pour tester le système complet.
"""

import os
import sys
import logging
import json
import argparse
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("max_sprint5.log")
    ]
)
logger = logging.getLogger(__name__)

# Importer les composants
from response_generation.response_generator import get_response_generator
from response_generation.quality_control import get_quality_control

class MaxApplication:
    """Application principale pour Max RAG Multimodal."""
    
    def __init__(self):
        """Initialise l'application avec tous les composants nécessaires."""
        # Initialiser les services
        logger.info("Initialisation des services...")
        self.response_generator = get_response_generator()
        self.quality_control = get_quality_control()
        
        logger.info("Application Max initialisée avec succès!")
    
    def process_query(
        self,
        query: str,
        query_type: str = "question",
        model: Optional[str] = None,
        temperature: float = 0.3,
        check_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Traite une requête complète.
        
        Args:
            query: La requête de l'utilisateur
            query_type: Le type de requête (question, cours, concept, json, problème)
            model: Le modèle à utiliser (optionnel)
            temperature: La température pour la génération
            check_quality: Si True, vérifie la qualité de la réponse
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées
        """
        logger.info(f"Traitement de la requête: {query} (type: {query_type})")
        
        # Générer la réponse
        response_result = self.response_generator.generate_response(
            query=query,
            query_type=query_type,
            model=model,
            temperature=temperature
        )
        
        # Vérifier la qualité si demandé
        if check_quality:
            quality_results = self.quality_control.check_response_quality(
                response=response_result["response"],
                query_type=query_type
            )
            
            # Ajouter les résultats de qualité à la réponse
            response_result["quality"] = quality_results
            
            # Régénérer la réponse si la qualité est insuffisante
            if not quality_results["is_acceptable"] and model is None:
                logger.warning(f"Qualité insuffisante (score: {quality_results['quality_score']}). Régénération avec un modèle plus avancé...")
                
                # Utiliser un modèle plus avancé pour la seconde tentative
                advanced_model = os.getenv("ADVANCED_MODEL", "gpt-4o")
                
                # Régénérer la réponse avec le modèle avancé
                response_result = self.response_generator.generate_response(
                    query=query,
                    query_type=query_type,
                    model=advanced_model,
                    temperature=max(0.2, temperature - 0.1)  # Réduire légèrement la température
                )
                
                # Vérifier à nouveau la qualité
                quality_results = self.quality_control.check_response_quality(
                    response=response_result["response"],
                    query_type=query_type
                )
                
                # Mettre à jour les résultats de qualité
                response_result["quality"] = quality_results
                response_result["regenerated"] = True
        
        return response_result
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Liste les modèles disponibles via OpenRouter.
        
        Returns:
            Liste des modèles disponibles
        """
        return self.response_generator.get_available_models()
    
    def interactive_session(self):
        """Lance une session interactive pour tester l'application."""
        print("\n" + "=" * 50)
        print("  MAX RAG MULTIMODAL - SESSION INTERACTIVE")
        print("=" * 50)
        
        print("\nBienvenue dans la session interactive de Max !")
        print("Vous pouvez poser des questions sur l'électronique.")
        print("Commandes spéciales :")
        print("  !exit - Quitter la session")
        print("  !models - Lister les modèles disponibles")
        print("  !type:<type> - Changer le type de requête (question, json, concept, cours, probleme)")
        print("  !model:<nom> - Changer le modèle LLM")
        print("  !temp:<valeur> - Changer la température (0.0-1.0)")
        
        # Paramètres par défaut
        query_type = "question"
        model = None
        temperature = 0.3
        
        while True:
            print("\n" + "-" * 50)
            prompt = f"[{query_type}] > "
            if model:
                prompt = f"[{query_type}, {model}] > "
            
            # Obtenir la requête
            query = input(prompt)
            
            # Traiter les commandes spéciales
            if query.lower() == "!exit":
                print("Au revoir !")
                break
            elif query.lower() == "!models":
                models = self.list_available_models()
                print("\nModèles disponibles :")
                if isinstance(models, list):
                    for i, m in enumerate(models):
                        if i >= 10:  # Limiter à 10 modèles
                            break
                        print(f"- {m.get('id', 'N/A')}")
                else:
                    print(f"Format des modèles: {type(models)}")
                    print(f"Contenu: {models}")
                continue
            elif query.lower().startswith("!type:"):
                new_type = query.split(":", 1)[1].strip()
                if new_type in ["question", "json", "concept", "cours", "probleme"]:
                    query_type = new_type
                    print(f"Type de requête changé à: {query_type}")
                else:
                    print(f"Type de requête non reconnu: {new_type}")
                continue
            elif query.lower().startswith("!model:"):
                model = query.split(":", 1)[1].strip()
                if model.lower() == "default":
                    model = None
                print(f"Modèle changé à: {model or 'défaut'}")
                continue
            elif query.lower().startswith("!temp:"):
                try:
                    temp_value = float(query.split(":", 1)[1].strip())
                    if 0.0 <= temp_value <= 1.0:
                        temperature = temp_value
                        print(f"Température changée à: {temperature}")
                    else:
                        print("La température doit être entre 0.0 et 1.0")
                except ValueError:
                    print("Valeur de température invalide")
                continue
            
            # Traiter la requête normale
            if not query.strip():
                continue
                
            try:
                # Traiter la requête
                result = self.process_query(
                    query=query,
                    query_type=query_type,
                    model=model,
                    temperature=temperature
                )
                
                # Afficher la réponse
                print("\nRéponse de Max:")
                print("-" * 50)
                
                if isinstance(result["response"], dict):
                    # Formatage spécial pour les réponses JSON
                    print(json.dumps(result["response"], ensure_ascii=False, indent=2))
                else:
                    print(result["response"])
                
                # Afficher les métriques de qualité si disponibles
                if "quality" in result:
                    quality = result["quality"]
                    print("\nMétriques de qualité:")
                    print(f"- Score: {quality['quality_score']} (Acceptable: {'Oui' if quality['is_acceptable'] else 'Non'})")
                    
                    if quality["issues"]:
                        print("- Problèmes:")
                        for issue in quality["issues"]:
                            print(f"  * {issue}")
                
                # Afficher le modèle utilisé et le temps de traitement
                print("\nInformations:")
                print(f"- Modèle utilisé: {result.get('model_used', 'N/A')}")
                print(f"- Temps de traitement: {result.get('processing_time', 0):.2f} secondes")
                if result.get("regenerated"):
                    print("- La réponse a été régénérée pour améliorer la qualité")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
                print(f"\nDésolé, une erreur s'est produite: {str(e)}")

def main():
    """Fonction principale pour exécuter l'application."""
    parser = argparse.ArgumentParser(description="Application Max RAG Multimodal")
    parser.add_argument("--interactive", action="store_true", help="Lancer en mode interactif")
    parser.add_argument("--query", type=str, help="Requête à traiter")
    parser.add_argument("--type", type=str, default="question", 
                      choices=["question", "json", "concept", "cours", "probleme"],
                      help="Type de requête")
    parser.add_argument("--model", type=str, help="Modèle LLM à utiliser")
    parser.add_argument("--temp", type=float, default=0.3, help="Température (0.0-1.0)")
    
    args = parser.parse_args()
    
    try:
        # Initialiser l'application
        app = MaxApplication()
        
        if args.interactive:
            # Mode interactif
            app.interactive_session()
        elif args.query:
            # Mode requête unique
            result = app.process_query(
                query=args.query,
                query_type=args.type,
                model=args.model,
                temperature=args.temp
            )
            
            # Afficher la réponse
            if isinstance(result["response"], dict):
                print(json.dumps(result["response"], ensure_ascii=False, indent=2))
            else:
                print(result["response"])
        else:
            # Par défaut, lancer le mode interactif
            app.interactive_session()
            
    except Exception as e:
        logger.error(f"Erreur dans l'application principale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()