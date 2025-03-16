# scripts/test_api_directly.py
import os
import sys
import requests
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_encode_queries():
    """Teste directement l'API pour encoder des requêtes."""
    base_url = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
    url = f"{base_url}/encode_queries"
    
    # L'API attend peut-être une structure différente
    queries = ["Qu'est-ce qu'un condensateur ?"]
    
    # Essayons différents formats pour trouver celui qui fonctionne
    # Format 1: Envoi direct de la liste
    logger.info("Essai avec format 1: envoi direct de la liste")
    response1 = requests.post(
        url,
        json=queries,
        params={"dimension": 1536}
    )
    logger.info(f"Résultat format 1: {response1.status_code}, {response1.text if response1.status_code != 200 else 'OK'}")
    
    # Format 2: Avec une clé "queries"
    logger.info("Essai avec format 2: avec une clé 'queries'")
    response2 = requests.post(
        url,
        json={"queries": queries},
        params={"dimension": 1536}
    )
    logger.info(f"Résultat format 2: {response2.status_code}, {response2.text if response2.status_code != 200 else 'OK'}")
    
    # Si l'un des formats fonctionne, afficher les résultats
    if response1.status_code == 200:
        result = response1.json()
        logger.info(f"Format 1 réussi! Réponse reçue: {result.keys()}")
        logger.info(f"Dimension des embeddings: {len(result['embeddings'][0])}")
    elif response2.status_code == 200:
        result = response2.json()
        logger.info(f"Format 2 réussi! Réponse reçue: {result.keys()}")
        logger.info(f"Dimension des embeddings: {len(result['embeddings'][0])}")

def test_encode_documents(image_path):
    """Teste directement l'API pour encoder des documents."""
    base_url = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
    url = f"{base_url}/encode_documents"
    
    if not os.path.exists(image_path):
        logger.error(f"L'image n'existe pas: {image_path}")
        return
    
    logger.info(f"Utilisation de l'image: {image_path}")
    file_name = Path(image_path).name
    
    with open(image_path, 'rb') as f:
        files = [('files', (file_name, f, 'image/jpeg'))]
        
        logger.info(f"Envoi de la requête à {url} avec le fichier: {file_name}")
        
        response = requests.post(
            url,
            files=files,
            params={"dimension": 1536}
        )
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Réponse reçue: {result.keys()}")
        logger.info(f"Dimension des embeddings: {len(result['embeddings'][0])}")
    else:
        logger.error(f"Erreur: {response.status_code}, {response.text}")

# Modification de la fin du fichier scripts/test_api_directly.py

if __name__ == "__main__":
    print("Test direct de l'API d'embeddings")
    print("1. Tester l'encodage de requêtes")
    print("2. Tester l'encodage de documents")
    
    choice = input("Entrez votre choix (1-2): ")
    
    if choice == "1":
        test_encode_queries()
    elif choice == "2":
        # Chercher automatiquement une image dans le dossier data/images
        image_found = False
        for root, dirs, files in os.walk('data/images'):
            for file in files:
                if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg'):
                    image_path = os.path.join(root, file)
                    image_found = True
                    print(f"Image trouvée automatiquement: {image_path}")
                    break
            if image_found:
                break
        
        if not image_found:
            image_path = input("Entrez le chemin vers une image pour le test: ")
        
        test_encode_documents(image_path)
    else:
        print("Choix invalide")