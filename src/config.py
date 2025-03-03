# src/config.py
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Configuration embeddings
EMBEDDINGS_API_URL = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
EMBEDDINGS_DIMENSION = 1536

# Configuration du logger
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)