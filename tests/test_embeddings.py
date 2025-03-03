# tests/test_embeddings.py
import os
import asyncio
from src.embeddings.embeddings_client import EmbeddingsClient
from src.database.supabase_client import SupabaseManager
import logging
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

async def test_text_embeddings():
    try:
        # Initialiser le client d'embeddings
        embeddings_client = EmbeddingsClient()
        
        # Tester avec quelques textes
        test_texts = [
            "Ceci est un test sur les capteurs en électronique",
            "Les capteurs électroniques permettent de mesurer des grandeurs physiques"
        ]
        
        # Générer les embeddings
        embeddings = await embeddings_client.encode_text(test_texts)
        
        print(f"Generated {len(embeddings)} text embeddings")
        print(f"Dimension of embeddings: {len(embeddings[0])}")
        
        # Tester la similarité
        similarity = await embeddings_client.compute_similarity(embeddings[0], embeddings[1])
        print(f"Similarity between texts: {similarity:.4f}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

async def test_image_embeddings():
    try:
        # Initialiser le client d'embeddings
        embeddings_client = EmbeddingsClient()
        
        # Créer une image test
        img = Image.new('RGB', (100, 100), color = 'red')
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Générer l'embedding
        embeddings = await embeddings_client.encode_images([img_base64])
        
        if embeddings:
            print(f"Generated {len(embeddings)} image embeddings")
            print(f"Dimension of embeddings: {len(embeddings[0])}")
        else:
            print("Failed to generate image embeddings")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

async def main():
    print("\nTesting Text Embeddings...")
    print("="*50)
    await test_text_embeddings()
    
    print("\nTesting Image Embeddings...")
    print("="*50)
    await test_image_embeddings()

if __name__ == "__main__":
    asyncio.run(main())