# src/api/app.py
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn
import asyncio
from config.settings import settings

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("max_api.log")
    ]
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Configuration CORS pour permettre l'intégration avec le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour le logging des requêtes et le rate limiting
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware pour logger les requêtes et implémenter un rate limiter simple."""
    # Logging de la requête
    start_time = time.time()
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer la durée
    process_time = time.time() - start_time
    
    # Logger les infos
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.4f}s - "
        f"Client: {request.client.host}"
    )
    
    return response

# Importer les routeurs
from api.routers import queries, documents, embeddings, health

# Ajouter les routeurs à l'application
app.include_router(health.router, tags=["Santé"])
app.include_router(queries.router, tags=["Requêtes"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(embeddings.router, tags=["Embeddings"])

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'API"""
    logger.info(f"Démarrage de l'API {settings.API_TITLE} v{settings.API_VERSION}")
    
    # Vérifier que les répertoires nécessaires existent
    os.makedirs(settings.IMAGES_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_UPLOADS_DIR, exist_ok=True)
    
    # Vérifier la configuration
    required_env_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENROUTER_API_KEY"]
    missing_vars = [var for var in required_env_vars if not getattr(settings, var)]
    
    if missing_vars:
        logger.error(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")
        raise ValueError(f"Configuration incomplète, variables manquantes: {', '.join(missing_vars)}")
        
    logger.info("Configuration validée, API prête")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'API"""
    logger.info(f"Arrêt de l'API {settings.API_TITLE}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'exceptions global pour toutes les erreurs non gérées."""
    logger.error(f"Erreur non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne s'est produite. Veuillez réessayer plus tard."}
    )

def start():
    """Lance l'API avec uvicorn"""
    uvicorn.run(
        "api.app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.RELOAD
    )

if __name__ == "__main__":
    start()