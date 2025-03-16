import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.supabase_client import get_supabase_client
from src.api.openrouter_client import get_openrouter_client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_supabase_connection():
    """Teste la connexion à Supabase"""
    try:
        supabase = get_supabase_client()
        # Essayer de récupérer les données de la table courses
        response = supabase.table("courses").select("*").limit(1).execute()
        print(f"Connexion à Supabase réussie! Données récupérées: {response}")
        return True
    except Exception as e:
        print(f"Erreur de connexion à Supabase: {e}")
        return False

def test_openrouter_connection():
    """Teste la connexion à OpenRouter"""
    try:
        openrouter = get_openrouter_client()
        # Récupérer les modèles disponibles
        models = openrouter.get_available_models()
        print(f"Connexion à OpenRouter réussie! Modèles disponibles: {models}")
        return True
    except Exception as e:
        print(f"Erreur de connexion à OpenRouter: {e}")
        return False

if __name__ == "__main__":
    print("Test des connexions...")
    supabase_ok = test_supabase_connection()
    openrouter_ok = test_openrouter_connection()
    
    if supabase_ok and openrouter_ok:
        print("Toutes les connexions sont fonctionnelles!")
    else:
        print("Certaines connexions ont échoué. Veuillez vérifier les erreurs ci-dessus.")