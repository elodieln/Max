"""
Tests pour le générateur de réponses.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Charger les variables d'environnement
load_dotenv()

from src.response_generation.response_generator import get_response_generator
from src.response_generation.quality_control import get_quality_control

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_response_generation():
    """Teste la génération de réponses avec le système complet."""
    try:
        # Initialisation des services
        response_generator = get_response_generator()
        quality_control = get_quality_control()
        
        # Test avec une question simple
        query = "Qu'est-ce qu'un condensateur et comment fonctionne-t-il?"
        
        logger.info(f"Test de génération de réponse pour la requête: {query}")
        
        # Générer une réponse
        response_result = response_generator.generate_response(
            query=query,
            query_type="question",
            temperature=0.3
        )
        
        # Afficher la réponse
        logger.info("Réponse générée:")
        logger.info("-" * 50)
        logger.info(response_result["response"])
        logger.info("-" * 50)
        
        # Vérifier la qualité de la réponse
        quality_results = quality_control.check_response_quality(
            response=response_result["response"],
            query_type="question"
        )
        
        logger.info(f"Score de qualité: {quality_results['quality_score']}")
        
        if quality_results["issues"]:
            logger.warning("Problèmes identifiés:")
            for issue in quality_results["issues"]:
                logger.warning(f"- {issue}")
        
        if quality_results["warnings"]:
            logger.info("Avertissements:")
            for warning in quality_results["warnings"]:
                logger.info(f"- {warning}")
        
        if quality_results["suggestions"]:
            logger.info("Suggestions d'amélioration:")
            for suggestion in quality_results["suggestions"]:
                logger.info(f"- {suggestion}")
        
        # Test avec une requête de type JSON
        json_query = "Explique-moi les semi-conducteurs"
        
        logger.info(f"Test de génération de réponse JSON pour la requête: {json_query}")
        
        # Générer une réponse JSON
        json_response_result = response_generator.generate_response(
            query=json_query,
            query_type="json",
            temperature=0.2
        )
        
        # Afficher la réponse
        logger.info("Réponse JSON générée:")
        logger.info("-" * 50)
        if isinstance(json_response_result["response"], dict):
            from pprint import pprint
            pprint(json_response_result["response"])
        else:
            logger.info(json_response_result["response"])
        logger.info("-" * 50)
        
        # Vérifier la qualité de la réponse JSON
        json_quality_results = quality_control.check_response_quality(
            response=json_response_result["response"],
            query_type="json"
        )
        
        logger.info(f"Score de qualité JSON: {json_quality_results['quality_score']}")
        
        # Test de récupération des modèles disponibles
        available_models = response_generator.get_available_models()
        logger.info(f"Nombre de modèles disponibles: {len(available_models) if isinstance(available_models, list) else 'non disponible'}")
        if available_models and isinstance(available_models, list):
            logger.info("Modèles disponibles:")
            for i, model in enumerate(available_models):
                if i >= 5:  # Afficher seulement les 5 premiers
                    break
                logger.info(f"- {model.get('id', 'N/A')}")
        else:
            logger.info(f"Format des modèles disponibles: {type(available_models)}")
            logger.info(f"Contenu: {available_models}")
        
    except Exception as e:
        logger.error(f"Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_response_generation()