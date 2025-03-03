# tests/test_supabase.py
import os
from dotenv import load_dotenv
from src.database.supabase_client import SupabaseManager
from src.extractors.pdf_processor import PDFProcessor
import asyncio

load_dotenv()

async def test_connection():
    try:
        # Initialize the Supabase manager
        supabase_manager = SupabaseManager()
        
        # Test getting courses
        courses = await supabase_manager.get_courses()
        print(f"Successfully retrieved {len(courses)} courses")
        
        # Test getting vectors for the first course if any exists
        if courses:
            vectors = await supabase_manager.get_vectors_by_course_id(courses[0]['id'])
            print(f"Successfully retrieved {len(vectors)} vectors for course {courses[0]['id']}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")

async def test_pdf_storage():
    try:
        # Initialiser le client Supabase
        supabase = SupabaseManager()
        
        # Traiter le PDF
        pdf_path = os.path.join("data", "MAX - IA Gen (1).pdf")
        processor = PDFProcessor(pdf_path)
        chunks = processor.extract_content()
        
        # Stocker les chunks pour le cours existant
        course_name = "Du capteur à la mesure - Cours 1 - Capteurs et mesure"  # Nom exact de la BDD
        await supabase.store_chunks(course_name, chunks)
        print(f"Successfully stored {len(chunks)} chunks")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

async def clean_vectors():
    try:
        # Initialiser le client Supabase
        supabase = SupabaseManager()
        
        # Supprimer les vecteurs du cours ID 13
        await supabase.delete_vectors_by_course_id(13)
        print("Successfully cleaned vectors for course 13")
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

async def main():
    print("\nCleaning existing vectors...")
    print("="*50)
    await clean_vectors()
    
    print("\nTesting Supabase Connection...")
    print("="*50)
    await test_connection()
    
    print("\nTesting PDF Storage...")
    print("="*50)
    await test_pdf_storage()

if __name__ == "__main__":
    asyncio.run(main())