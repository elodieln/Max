# src/api/routers/health.py
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health")

class HealthResponse(BaseModel):
    status: str
    version: str
    api_name: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Vérification de la santé de l'API.
    """
    logger.info("Health check demandé")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_name": "Max RAG Multimodal API"
    }