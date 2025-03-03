# tests/test_pdf_processor.py
from src.extractors.pdf_processor import PDFProcessor
import logging
import os
from collections import Counter

logger = logging.getLogger(__name__)

def test_pdf_extraction():
    try:
        pdf_path = os.path.join("data", "MAX - IA Gen (1).pdf")
        
        processor = PDFProcessor(pdf_path)
        chunks = processor.extract_content()
        
        # Statistiques détaillées
        text_chunks = [c for c in chunks if c['type'] == 'text']
        image_chunks = [c for c in chunks if c['type'] == 'image']
        
        # Analyse des sections
        sections = Counter(chunk['metadata']['section'] for chunk in chunks if 'metadata' in chunk)
        
        # Analyse des types de contenu
        content_types = Counter(
            chunk['metadata']['content_type'] 
            for chunk in image_chunks 
            if 'metadata' in chunk
        )
        
        print("\nRésultats de l'extraction:")
        print("="* 50)
        print(f"Total de chunks : {len(chunks)}")
        print(f"Chunks de texte : {len(text_chunks)}")
        print(f"Chunks d'images : {len(image_chunks)}")
        
        print("\nDistribution des sections:")
        print("="* 50)
        for section, count in sections.most_common():
            print(f"- {section}: {count} chunks")
            
        print("\nTypes de contenu dans les images:")
        print("="* 50)
        for content_type, count in content_types.most_common():
            print(f"- {content_type}: {count} images")
        
        print("\nExemple de chunk texte avec métadonnées:")
        print("="* 50)
        if text_chunks:
            chunk = text_chunks[0]
            print("Contenu:", chunk['content'][:150], "...")
            print("Métadonnées:", chunk['metadata'])
            
    except Exception as e:
        logger.error(f"Error testing PDF extraction: {str(e)}")

if __name__ == "__main__":
    test_pdf_extraction()