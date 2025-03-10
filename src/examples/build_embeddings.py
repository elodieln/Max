import os
import asyncio
from dotenv import load_dotenv

# Importer la classe MultimodalRAG et le manager Supabase
from src.rag.multimodal_rag import MultimodalRAG
from src.database.supabase_client import SupabaseManager

async def rebuild_embeddings_for_all_courses():
    """
    1) Vide complètement la table 'vectors'
    2) Traite tous les PDFs du dossier 'data' (racine du projet)
       et reconstruit leurs embeddings en base Supabase
    """

    # 1) Vider la table 'vectors'
    supabase_client = SupabaseManager()
    # Supprimer toutes les lignes de la table 'vectors'
    # On peut utiliser la méthode table('vectors').delete() sans condition
    print("[INFO] Deleting all vectors from 'vectors' table...")
    supabase_client.supabase.table("vectors").delete().neq("id", 0).execute()
    print("[INFO] Table 'vectors' is now empty.\n")

    # 2) Parcourir tous les fichiers PDF du dossier 'data'
    data_folder = "data"
    pdf_files = [f for f in os.listdir(data_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("[WARNING] Aucun fichier PDF trouvé dans le dossier 'data'.")
        return

    # Initialiser le système RAG
    rag = MultimodalRAG()

    # Traiter chaque PDF
    for pdf_name in pdf_files:
        # Retirer l'extension .pdf pour obtenir le nom du cours
        course_name = pdf_name[:-4]

        pdf_path = os.path.join(data_folder, pdf_name)

        print(f"[INFO] Processing PDF '{pdf_name}' for course '{course_name}'...")

        # Appeler la méthode process_pdf pour extraire, encoder et stocker
        success = await rag.process_pdf(pdf_path, course_name)
        if success:
            print(f"[SUCCESS] Embeddings stored for '{pdf_name}'.\n")
        else:
            print(f"[ERROR] Failed to process '{pdf_name}'.\n")

if __name__ == "__main__":
    # Charger les variables d'environnement (SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENROUTER_API_KEY, etc.)
    load_dotenv()
    asyncio.run(rebuild_embeddings_for_all_courses())
