# examples/test_openrouter_rag.py
import os
import asyncio
import logging
from dotenv import load_dotenv
from src.rag.multimodal_rag import MultimodalRAG

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

async def test_openrouter_rag():
    """Test le système RAG multimodal avec OpenRouter"""
    try:
        # Vérifier que la clé API est disponible
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.error("OPENROUTER_API_KEY environment variable not set")
            return
            
        # Initialiser le système RAG
        rag = MultimodalRAG()
        
        # Traitement du PDF "MAX - IA Gen (1).pdf"
        pdf_path = os.path.join("data", "MAX - IA Gen (1).pdf")
        course_name = "Test Multimodal RAG"  # Nom visible dans l'interface
        course_id = 19  # ID du cours dans la base de données
                
        # Vérifier que le fichier existe
        if not os.path.exists(pdf_path):
            logger.error(f"Le fichier PDF n'existe pas: {pdf_path}")
            return
                
        logger.info(f"Traitement du PDF: {pdf_path}")
        success = await rag.process_pdf(pdf_path, course_name, course_id)
        
        if not success:
            logger.error("Échec du traitement du PDF")
            return
        
        # Une fois le PDF traité, vous pouvez poser des questions
        questions = [
            "Quels sont les éléments constitutifs de la chaîne d’acquisition de données présentée ?",
            "Quelles sont les différences principales entre un capteur actif et un capteur passif ?",
            "Comment le conditionnement d’un signal est-il réalisé dans le contexte de cette présentation ?"
        ]
        
        for question in questions:
            print("\n" + "="*50)
            print("QUESTION:", question)
            print("="*50)
            
            result = await rag.answer_query(question)
            
            print("RÉPONSE:")
            print(result["answer"])
            print("\n" + "="*20 + " SOURCES " + "="*20)
            for i, source in enumerate(result["sources"], 1):
                print(f"  {i}. Type: {source['chunk_type']}, Page: {source['page_number']}, Similarité: {source['similarity']:.4f}")
                if "text_preview" in source:
                    print(f"     Texte: {source['text_preview']}")
                print()
        
    except Exception as e:
        logger.error(f"Erreur dans le test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_openrouter_rag())