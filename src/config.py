# src/config.py
import os
from dotenv import load_dotenv
from src.utils.custom_logging import configure_logging

# Chargement des variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Configuration embeddings
EMBEDDINGS_API_URL = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
EMBEDDINGS_DIMENSION = 1536

# Configuration pour OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Configuration du logger
log_system_message = configure_logging()

# Variable globale pour accéder à la fonction de log système
def system_log(message, level="INFO"):
    """Wrapper pour la fonction log_system_message"""
    log_system_message(message, level)