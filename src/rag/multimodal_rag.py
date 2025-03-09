# src/rag/multimodal_rag.py
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import json

from src.extractors.pdf_processor import PDFProcessor
from src.embeddings.embeddings_client import EmbeddingsClient
from src.database.supabase_client import SupabaseManager
from src.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class MultimodalRAG:
    """Système RAG multimodal pour les cours d'électronique"""
    
    def __init__(self):
        self.embeddings_client = EmbeddingsClient()
        self.supabase_client = SupabaseManager()
        self.gemini_client = GeminiClient()
        logger.info("Initialized MultimodalRAG system")
    
    async def process_pdf(self, pdf_path: str, course_name: str, course_id=None):
        """
        Traite un PDF et stocke ses chunks dans la base de données
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            course_name: Nom du cours associé au PDF
            course_id: ID du cours (optionnel)
            
        Returns:
            True si le traitement est réussi, False sinon
        """
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return False
            
            # Créer le processeur PDF
            processor = PDFProcessor(pdf_path)
            
            # Extraire le contenu
            logger.info(f"Extracting content from PDF: {pdf_path}")
            chunks = processor.extract_content()
            
            # Utiliser l'ID du cours si fourni, sinon rechercher par nom
            if course_id is not None:
                logger.info(f"Using provided course ID: {course_id}")
            else:
                # Vérifier si le cours existe déjà
                try:
                    course_id = await self.supabase_client.get_course_id(course_name)
                    logger.info(f"Course '{course_name}' exists with ID {course_id}")
                except ValueError:
                    logger.error(f"Course '{course_name}' not found. Please create it first.")
                    return False
            
            # Supprimer les vecteurs existants
            logger.info(f"Deleting existing vectors for course {course_id}")
            await self.supabase_client.delete_vectors_by_course_id(course_id)
            
            # Stocker les chunks avec leurs embeddings
            logger.info(f"Storing {len(chunks)} chunks with embeddings")
            await self.supabase_client.store_chunks_with_embeddings(
                course_name, 
                chunks, 
                self.embeddings_client
            )
            
            # Analyse supplémentaire des schémas électroniques
            await self._analyze_electronic_schemas(chunks, course_id)
            
            logger.info(f"Successfully processed PDF for course '{course_name}'")
            return True
                
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return False
    
    async def _analyze_electronic_schemas(self, chunks: List[Dict[str, Any]], course_id: int) -> None:
        """
        Analyse les schémas électroniques dans les chunks d'images
        
        Args:
            chunks: Liste des chunks extraits du PDF
            course_id: ID du cours
        """
        # Filtrer les chunks qui pourraient contenir des schémas électroniques
        schema_candidates = []
        
        for chunk in chunks:
            if chunk['type'] == 'image':
                metadata = chunk.get('metadata', {})
                # Vérifier si c'est potentiellement un schéma
                if metadata.get('has_diagram') or metadata.get('content_type') == 'diagram':
                    schema_candidates.append(chunk)
            elif chunk['type'] == 'mixed':
                metadata = chunk.get('metadata', {})
                if metadata.get('has_diagram') or metadata.get('content_type') == 'diagram':
                    schema_candidates.append(chunk)
        
        num_candidates = len(schema_candidates)
        logger.info(f"Found {num_candidates} potential electronic schema candidates")
        
        # Limiter le nombre de messages de progression
        progress_interval = max(1, num_candidates // 5)  # Afficher seulement 5 messages de progression
        
        # Analyser chaque schéma potentiel
        for i, chunk in enumerate(schema_candidates):
            try:
                # N'afficher la progression qu'à certains intervalles ou au début/fin
                if i == 0 or i == num_candidates - 1 or i % progress_interval == 0:
                    logger.info(f"Analyzing schemas progress: {i+1}/{num_candidates}")
                
                # Extraire le contexte textuel pour les chunks mixtes
                context = None
                if chunk['type'] == 'mixed' and 'content' in chunk:
                    context = chunk['content']
                
                # Obtenir les données d'image
                image_data = chunk.get('image_data') if chunk['type'] == 'mixed' else chunk.get('content')
                
                if not image_data:
                    continue
                
                # Analyser le schéma sans logger chaque analyse
                analysis = await self.gemini_client.analyze_schema(image_data, context)
                
                # Ne pas logger chaque analyse stockée
                # logger.info(f"Analysis stored for schema {i+1}")
                
            except Exception as e:
                # Ne pas enregistrer chaque erreur individuelle
                if not hasattr(MultimodalRAG, "_schema_error_reported"):
                    MultimodalRAG._schema_error_reported = True
                    logger.error(f"Error during schema analysis: {str(e)}")
    
    async def answer_query(self, query: str, course_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Répond à une requête utilisateur en utilisant le système RAG
        
        Args:
            query: Requête de l'utilisateur
            course_ids: Liste optionnelle d'IDs de cours à rechercher (si None, recherche dans tous les cours)
            
        Returns:
            Dict contenant la réponse et les sources utilisées
        """
        try:
            # Étape 1: Réécrire la requête pour améliorer la recherche
            rewritten_query = await self.gemini_client.rewrite_query(query)
            
            # Étape 2: Générer l'embedding de la requête
            query_embedding = await self.embeddings_client.encode_text([rewritten_query])
            
            # Étape 3: Rechercher les chunks pertinents
            top_k = 5  # Nombre de résultats à récupérer
            results = await self.supabase_client.search_vectors(query_embedding[0], top_k=top_k)
            
            if not results:
                return {
                    "answer": "Je n'ai pas trouvé d'information pertinente pour répondre à cette question.",
                    "sources": []
                }
            
            # Étape 4: Vérifier si la requête concerne potentiellement un schéma électronique
            is_schema_query = self._is_schema_related_query(query)
            
            # Étape 5: Si c'est une requête sur un schéma, prioriser les chunks d'images et mixtes
            relevant_chunks = []
            
            if is_schema_query:
                # Prioriser les chunks contenant des images/schémas
                for result in results:
                    if result['chunk_type'] in ['image', 'mixed']:
                        relevant_chunks.append(result)
                
                # Ajouter des chunks textuels si nécessaire
                for result in results:
                    if result['chunk_type'] == 'text' and len(relevant_chunks) < top_k:
                        relevant_chunks.append(result)
            else:
                # Ordre standard pour les requêtes textuelles
                relevant_chunks = results
            
            # Étape 6: Générer la réponse avec Gemini
            answer = await self.gemini_client.generate_response(query, relevant_chunks)
            
            # Étape 7: Préparer les sources
            sources = []
            for chunk in relevant_chunks:
                source = {
                    "chunk_type": chunk['chunk_type'],
                    "page_number": chunk['page_number'],
                    "course_id": chunk['course_id'],
                    "similarity": chunk['similarity'],
                }
                
                if chunk['chunk_type'] in ['text', 'mixed']:
                    # Limiter la taille du texte pour la source
                    text = chunk['chunk_text']
                    source["text_preview"] = text[:200] + "..." if len(text) > 200 else text
                
                if chunk['chunk_type'] in ['image', 'mixed']:
                    source["has_image"] = bool(chunk.get('image_data'))
                
                sources.append(source)
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return {
                "answer": f"Désolé, une erreur s'est produite lors du traitement de votre requête.",
                "sources": []
            }
    
    def _is_schema_related_query(self, query: str) -> bool:
        """
        Détermine si une requête est liée à un schéma électronique
        
        Args:
            query: Requête de l'utilisateur
            
        Returns:
            True si la requête est probablement liée à un schéma, False sinon
        """
        # Mots-clés associés aux schémas électroniques
        schema_keywords = [
            'schéma', 'circuit', 'diagramme', 'montage',
            'transistor', 'résistance', 'condensateur', 'diode',
            'amplificateur', 'filtre', 'oscillateur',
            'visualiser', 'afficher', 'montrer', 'expliquer le circuit'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in schema_keywords)