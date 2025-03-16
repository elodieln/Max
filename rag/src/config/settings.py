# src/config/settings.py
import os
from pydantic_settings import BaseSettings  # Notez le changement ici
from typing import Optional, Dict, Any, List

class Settings(BaseSettings):
    """Configuration de l'application."""
    
    # Informations de l'API
    API_TITLE: str = "Max RAG Multimodal API"
    API_DESCRIPTION: str = "API pour l'assistant IA Max, conçu pour aider les élèves en école d'ingénieur en électronique"
    API_VERSION: str = "1.0.0"
    
    # Connexion Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Connexion OpenRouter
    OPENROUTER_API_KEY: str
    DEFAULT_MODEL: str = "gpt-3.5-turbo-16k"
    ADVANCED_MODEL: str = "gpt-4o"
    
    # API RAG Multimodal
    RAG_API_URL: str = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
    
    # Configuration des stockages
    IMAGES_DIR: str = "data/images"
    TEMP_UPLOADS_DIR: str = "temp_uploads"
    
    # Configuration de l'API
    CORS_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    RELOAD: bool = True
    
    # Limites
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 Mo
    RATE_LIMIT_CALLS: int = 60  # Nombre d'appels
    RATE_LIMIT_PERIOD: int = 60  # Période en secondes
    
    class Config:
        env_file = ".env"

# Instance de configuration
settings = Settings()