# tests/test_multimodal_rag.py
import os
import asyncio
import sys
import logging
from src.extractors.pdf_processor import PDFProcessor
from src.embeddings.embeddings_client import EmbeddingsClient
from src.database.supabase_client import SupabaseManager

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_multimodal_rag():
    try:
        # Initialiser les clients
        embeddings_client = EmbeddingsClient()
        supabase_client = SupabaseManager()
        
        # Traiter le PDF
        pdf_path = os.path.join("data", "MAX - IA Gen (1).pdf")  # Ajustez le chemin si nécessaire
        processor = PDFProcessor(pdf_path)
        
        logger.info("Extracting content from PDF...")
        chunks = processor.extract_content()
        
        # Analyser les types de chunks
        text_chunks = [c for c in chunks if c['type'] == 'text']
        image_chunks = [c for c in chunks if c['type'] == 'image']
        mixed_chunks = [c for c in chunks if c['type'] == 'mixed']
        
        logger.info(f"Extracted {len(chunks)} total chunks:")
        logger.info(f"- {len(text_chunks)} text chunks")
        logger.info(f"- {len(image_chunks)} image chunks")
        logger.info(f"- {len(mixed_chunks)} mixed chunks")
        
        # Demander confirmation à l'utilisateur
        course_name = "Test Multimodal RAG"  # Ajustez selon vos besoins
        response = input(f"Stocker les chunks pour le cours '{course_name}'? (y/n): ")
        
        if response.lower() == 'y':
            logger.info(f"Storing chunks with embeddings for course '{course_name}'...")
            
            # Vérifier si le cours existe
            try:
                course_id = await supabase_client.get_course_id(course_name)
                # Supprimer les anciens vecteurs si le cours existe
                logger.info(f"Course '{course_name}' exists with ID {course_id}. Cleaning old vectors...")
                await supabase_client.delete_vectors_by_course_id(course_id)
            except ValueError:
                logger.info(f"Course '{course_name}' doesn't exist. Please create it first.")
                return
            
            # Stocker les chunks avec embeddings
            await supabase_client.store_chunks_with_embeddings(course_name, chunks, embeddings_client)
            logger.info("Storage completed successfully!")
            
            # Tester la recherche
            test_query = "Présentation du projet MAX pour l'électronique"
            logger.info(f"Testing search with query: '{test_query}'")
            
            # Générer l'embedding de la requête
            query_embedding = await embeddings_client.encode_text([test_query])
            
            # Rechercher les documents similaires
            results = await supabase_client.search_vectors(query_embedding[0], top_k=3)
            
            if results:
                logger.info(f"Found {len(results)} matching documents:")
                for i, result in enumerate(results):
                    logger.info(f"Match {i+1}:")
                    logger.info(f"  Similarity: {result['similarity']:.4f}")
                    logger.info(f"  Type: {result['chunk_type']}")
                    if result['chunk_type'] in ['text', 'mixed']:
                        logger.info(f"  Text: {result['chunk_text'][:100]}...")
                    if result['chunk_type'] in ['image', 'mixed']:
                        logger.info(f"  Has image: Yes")
            else:
                logger.info("No matching documents found")
        else:
            logger.info("Storage cancelled by user")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multimodal_rag())