import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.supabase_client import get_supabase_client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_supabase_tables():
    """Teste l'existence des tables dans Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Vérifier la table pages
        try:
            response = supabase.table("pages").select("*").limit(1).execute()
            print("✅ Table 'pages' existe")
        except Exception as e:
            print(f"❌ Erreur avec la table 'pages': {e}")
        
        # Vérifier la table page_embeddings
        try:
            response = supabase.table("page_embeddings").select("*").limit(1).execute()
            print("✅ Table 'page_embeddings' existe")
        except Exception as e:
            print(f"❌ Erreur avec la table 'page_embeddings': {e}")
        
        # Vérifier la table courses (devrait déjà exister)
        try:
            response = supabase.table("courses").select("*").limit(1).execute()
            print("✅ Table 'courses' existe")
        except Exception as e:
            print(f"❌ Erreur avec la table 'courses': {e}")
            
    except Exception as e:
        print(f"Erreur de connexion à Supabase: {e}")

if __name__ == "__main__":
    print("Test des tables Supabase...")
    test_supabase_tables()