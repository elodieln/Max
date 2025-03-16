# tests/test_openrouter.py
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter les répertoires au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from api.openrouter_client import get_openrouter_client

def test_openrouter_client():
    try:
        # Récupérer le client OpenRouter
        client = get_openrouter_client()
        
        print("Client OpenRouter initialisé avec succès.")
        print(f"API Key: {'*' * (len(os.getenv('OPENROUTER_API_KEY', '')) - 4)}...{'*' * 4}")
        print(f"Base URL: {client.base_url}")
        print(f"Modèle par défaut: {client.default_model}")
        
        # Tester la récupération des modèles
        print("\nRécupération des modèles disponibles...")
        models = client.get_available_models()
        
        if isinstance(models, list):
            print(f"Nombre de modèles disponibles: {len(models)}")
            if len(models) > 0:
                print(f"Premier modèle: {models[0].get('id', 'N/A')}")
        else:
            print("test")
            #print(f"Réponse inattendue: {models}")
            
        # Tester une génération simple
        print("\nTest de génération de réponse...")
        messages = [
            {"role": "system", "content": "Vous êtes un assistant utile."},
            {"role": "user", "content": "Bonjour, comment ça va?"}
        ]
        
        response = client.generate_response(messages, max_tokens=50)
        print(f"Réponse générée: {response}")
        
        print("\n✅ Tests OpenRouter réussis!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests OpenRouter: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Test du client OpenRouter...")
    test_openrouter_client()