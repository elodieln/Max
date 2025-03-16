# src/main_api.py
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter les répertoires au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Ajoute src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Ajoute le répertoire racine

# Importer l'application API et la démarrer
from api.app import start

if __name__ == "__main__":
    start()