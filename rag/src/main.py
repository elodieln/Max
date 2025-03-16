import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def main():
    """Point d'entrée principal du programme"""
    print("Démarrage du RAG multimodal pour Max")
    print(f"Environnement configuré avec succès")
    print(f"URL Supabase: {os.getenv('SUPABASE_URL')}")
    print(f"OpenRouter configuré: {'Oui' if os.getenv('OPENROUTER_API_KEY') else 'Non'}")
    print(f"Modèle par défaut: {os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo-16k')}")
    
    # Ici, nous ajouterons plus tard le code pour démarrer le système complet
    print("Le système est prêt à être utilisé.")

if __name__ == "__main__":
    main()