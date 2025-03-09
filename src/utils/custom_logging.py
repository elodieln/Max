# src/utils/custom_logging.py
import logging
import os

def configure_logging():
    """Configure le système de logging pour réduire la verbosité"""
    
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configuration du handler pour le fichier
    file_handler = logging.FileHandler('logs/max_app.log')
    file_handler.setLevel(logging.DEBUG)  # Tout est loggé dans le fichier
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Configuration du handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Seulement les warnings+ dans la console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Configuration du logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Supprimer les handlers existants pour éviter les doublons
    if root_logger.handlers:
        root_logger.handlers = []
    
    # Ajouter les handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configuration spécifique par module
    logging.getLogger('src.rag.multimodal_rag').setLevel(logging.INFO)
    logging.getLogger('src.database.supabase_client').setLevel(logging.WARNING)
    logging.getLogger('src.embeddings.embeddings_client').setLevel(logging.WARNING)
    logging.getLogger('src.llm.gemini_client').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('src.extractors.pdf_processor').setLevel(logging.WARNING)
    
    # Classe filtre pour éviter les messages répétitifs
    class DuplicateFilter(logging.Filter):
        def __init__(self, name=''):
            super().__init__(name)
            self.seen = set()
        
        def filter(self, record):
            # Créer une clé unique basée sur le module, le niveau et le message
            key = (record.levelno, record.getMessage())
            if key in self.seen:
                return False
            self.seen.add(key)
            return True
    
    # Ajouter le filtre pour éviter les messages répétés
    duplicate_filter = DuplicateFilter()
    console_handler.addFilter(duplicate_filter)
    
    # Retourner une fonction pour ajouter des messages système au format propre
    def log_system_message(message, level=logging.INFO):
        """Affiche un message système formaté proprement"""
        if level == logging.INFO:
            print(f"\n[INFO] {message}")
        elif level == logging.WARNING:
            print(f"\n[WARNING] {message}")
        elif level == logging.ERROR:
            print(f"\n[ERROR] {message}")
        elif level == logging.DEBUG:
            print(f"\n[DEBUG] {message}")
    
    return log_system_message

# Fonction pour des messages de progression clairs
def log_progress(current, total, prefix='Progress', suffix='Complete', decimals=1, length=50, fill='█'):
    """
    Affiche une barre de progression dans la console
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    # Nouvelle ligne après complétion
    if current == total:
        print()