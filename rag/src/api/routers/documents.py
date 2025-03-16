# src/api/routers/documents.py
import logging
import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from processing.pdf_extractor import PDFExtractor
from storage.supabase_client import get_supabase_client
from embeddings.embedding_generator import get_embedding_generator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents")

class ProcessResponse(BaseModel):
    course_id: int
    pages_processed: int
    embeddings_generated: int
    success: bool
    message: str

@router.post("/process", response_model=ProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    course_id: Optional[int] = Form(None),
    course_name: Optional[str] = Form(None),
    year: Optional[str] = Form("ING1")
):
    """
    Traite un document PDF et génère des embeddings pour chaque page.
    
    - Si course_id est fourni, le document sera associé à ce cours existant
    - Sinon, si course_name est fourni, un nouveau cours sera créé
    - Le paramètre year doit être l'un des suivants: ING1, ING2, ING3
    """
    try:
        logger.info(f"Traitement du document {file.filename}")
        
        # Vérifier que le fichier est un PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format PDF")
        
        # Vérifier que year est valide
        valid_years = ["ING1", "ING2", "ING3"]
        if year not in valid_years:
            raise HTTPException(status_code=400, detail=f"Le champ 'year' doit être l'un des suivants: {', '.join(valid_years)}")
        
        # Créer un répertoire temporaire pour le PDF
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # Enregistrer le fichier PDF
        with open(pdf_path, "wb") as pdf_file:
            shutil.copyfileobj(file.file, pdf_file)
        
        # Initialiser les clients
        supabase = get_supabase_client()
        extractor = PDFExtractor()
        embedding_generator = get_embedding_generator()
        
        # Si course_id n'est pas fourni, vérifier si un nouveau cours doit être créé
        if not course_id and course_name:
            # Créer un nouveau cours
            course_data = {
                "name": course_name,
                "pdf_url": file.filename,  # Nous stockons juste le nom du fichier
                "year": year
            }
            
            logger.info(f"Création d'un nouveau cours: {course_name}")
            result = supabase.table("courses").insert(course_data).execute()
            
            if result.data and len(result.data) > 0:
                course_id = result.data[0]["id"]
                logger.info(f"Nouveau cours créé avec l'ID: {course_id}")
            else:
                raise HTTPException(status_code=500, detail="Impossible de créer le cours")
        elif not course_id:
            raise HTTPException(status_code=400, detail="Vous devez fournir course_id ou course_name")
        
        # Extraire les pages du PDF
        pages_info = extractor.extract_from_pdf(pdf_path, course_id)
        
        if not pages_info:
            raise HTTPException(status_code=500, detail="Échec de l'extraction du PDF")
        
        # Enregistrer les pages dans Supabase
        page_ids = extractor.save_pages_to_supabase(pages_info, supabase)
        
        if not page_ids:
            raise HTTPException(status_code=500, detail="Échec de l'enregistrement des pages dans Supabase")
        
        # Préparation des infos pour la génération d'embeddings
        # On reconstruit la liste des infos avec juste les champs nécessaires
        pages_for_embeddings = [
            {"id": page_id, "image_path": pages_info[i]["image_path"]}
            for i, page_id in enumerate(page_ids)
        ]
        
        # Générer les embeddings
        logger.info(f"Génération d'embeddings pour {len(pages_for_embeddings)} pages")
        successful_embeddings = embedding_generator.generate_and_store_embeddings(pages_for_embeddings)
        
        return {
            "course_id": course_id,
            "pages_processed": len(page_ids),
            "embeddings_generated": len(successful_embeddings),
            "success": True,
            "message": f"Document traité avec succès. {len(page_ids)} pages extraites, {len(successful_embeddings)} embeddings générés."
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du document: {str(e)}")
    finally:
        # Nettoyer le fichier temporaire
        try:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
                logger.info(f"Fichier temporaire supprimé: {pdf_path}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du fichier temporaire: {str(e)}")

@router.get("/courses", response_model=List[Dict[str, Any]])
async def list_courses():
    """
    Liste tous les cours disponibles.
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("courses").select("*").order("created_at", desc=True).execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des cours: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des cours: {str(e)}")