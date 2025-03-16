import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class SupabaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialiser la connexion à Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Les variables d'environnement SUPABASE_URL et SUPABASE_KEY doivent être définies")
        
        self.client = create_client(supabase_url, supabase_key)
        print("Connexion à Supabase initialisée avec succès")
    
    def get_client(self) -> Client:
        """Retourne le client Supabase"""
        if not self.client:
            self.initialize()
        return self.client

# Fonction pour obtenir une instance du client Supabase
def get_supabase_client() -> Client:
    return SupabaseClient().get_client()