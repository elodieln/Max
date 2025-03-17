import os
import asyncio
from dotenv import load_dotenv
from src.rag.multimodal_rag import MultimodalRAG

async def process_single_document():
    # 1) Vider complètement la table vectors
    from src.database.supabase_client import SupabaseManager
    supabase_client = SupabaseManager()
    print("[INFO] Vider la table 'vectors'...")
    supabase_client.supabase.table("vectors").delete().neq("id", 0).execute()
    print("[INFO] Table 'vectors' vidée.\n")

    # 2) Spécifier le document à traiter
    data_folder = "data"
    pdf_filename = "amphi - Cours2 - Semi-conducteurs et jonction PN.pdf"
    course_name = pdf_filename[:-4]  # on suppose que le nom du cours correspond au nom du fichier sans l'extension
    pdf_path = os.path.join(data_folder, pdf_filename)
    
    # Vérifier que le fichier existe
    if not os.path.exists(pdf_path):
        print(f"[ERROR] Le fichier PDF '{pdf_filename}' est introuvable dans le dossier '{data_folder}'.")
        return

    # 3) Initialiser le système RAG
    rag = MultimodalRAG()
    
    # 4) Traiter le document et stocker les embeddings
    print(f"[INFO] Traitement du PDF '{pdf_filename}' pour le cours '{course_name}'...")
    success = await rag.process_pdf(pdf_path, course_name)
    if success:
        print(f"[SUCCESS] Embeddings stockés pour '{pdf_filename}'.\n")
    else:
        print(f"[ERROR] Échec du traitement de '{pdf_filename}'.\n")
    
    # 5) Optionnel : Afficher quelques chunks extraits pour vérifier leur contenu
    # Pour cela, nous allons utiliser le PDFProcessor directement
    from src.extractors.pdf_processor import PDFProcessor
    processor = PDFProcessor(pdf_path)
    chunks = processor.extract_content()
    print(f"[INFO] Nombre total de chunks extraits : {len(chunks)}")
    """
    for i, chunk in enumerate(chunks[:5], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Type: {chunk['type']}, Page: {chunk['page_number']}")
        preview = chunk.get('content', '')[:300]
        print("Contenu (premiers 300 caractères) :")
        print(preview)

    # Filtrer et afficher les chunks relatifs au dopage
    doping_keywords = ["dopage", "dopés", "phosphore", "bor", "dopant", "donneur", "accepteur", "impuretés"]
    doping_chunks = [chunk for chunk in chunks if any(keyword.lower() in chunk.get('content', '').lower() for keyword in doping_keywords)]

    print(f"\n[INFO] Nombre de chunks relatifs au dopage: {len(doping_chunks)}")
    for i, chunk in enumerate(doping_chunks, 1):
        print(f"\n--- Doping Chunk {i} ---")
        print(f"Type: {chunk['type']}, Page: {chunk['page_number']}")
        preview = chunk.get('content', '')[:300]
        print("Contenu (premiers 300 caractères) :")
        print(preview)
        """
    

    
if __name__ == "__main__":
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(process_single_document())
