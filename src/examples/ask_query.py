import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from dotenv import load_dotenv
from src.rag.multimodal_rag import MultimodalRAG

# Importer les outils de Rich pour une interface agréable
from rich.console import Console
from rich.prompt import Prompt



async def interactive_query():
    # Charger les variables d'environnement
    load_dotenv()
    
    console = Console()
    # Initialiser le système RAG
    rag = MultimodalRAG()
    
    console.print("[bold green]Système de Recherche d'Informations Multimodales[/bold green]")
    console.print("Tapez votre question (ou 'exit' pour quitter) :\n")
    
    while True:
        query = Prompt.ask("[bold blue]Votre question[/bold blue]")
        if query.lower() in ["exit", "quit"]:
            console.print("[bold magenta]Au revoir ![/bold magenta]")
            break
        
        console.print("[bold yellow]En cours de traitement...[/bold yellow]")
        result = await rag.answer_query(query)
        
        answer = result.get("answer", "Aucune réponse n'a été trouvée.")
        sources = result.get("sources", [])
        
        console.print("\n[bold green]Réponse:[/bold green] " + answer + "\n")
        console.print("[bold cyan]Sources:[/bold cyan]")
        if sources:
            for i, source in enumerate(sources, 1):
                console.print(f"{i}. [italic]Type:[/italic] {source.get('chunk_type')} - [italic]Page:[/italic] {source.get('page_number')} - [italic]Similarité:[/italic] {source.get('similarity'):.4f}")
                text_preview = source.get("text_preview", "")
                if text_preview:
                    console.print(f"    [dim]{text_preview}[/dim]")
        else:
            console.print("Aucune source trouvée.")
        
        console.print("\n" + "-"*50 + "\n")
        
if __name__ == "__main__":
    asyncio.run(interactive_query())
