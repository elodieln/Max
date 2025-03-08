# Feuille de Route Détaillée - Projet MAX RAG Multimodal

## PHASE 1 : Infrastructure et Configuration (1-2 semaines)

### 1.1 Configuration de l'Environnement de Développement
- [ ] Création d'un environnement virtuel Python
  ```bash
  python -m venv venv
  source venv/bin/activate  # Unix
  .\venv\Scripts\activate   # Windows
  ```
- [ ] Installation des dépendances
  ```bash
  pip install supabase pypdf python-dotenv numpy redis pillow torch transformers
  ```
- [ ] Configuration des variables d'environnement
  ```env
  SUPABASE_URL=your_url
  SUPABASE_KEY=your_key
  GEMINI_API_KEY=your_key
  REDIS_URL=your_redis_url
  ```

### 1.2 Configuration Supabase
- [ ] Vérification de l'extension pgvector
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```
- [ ] Création des index pour optimisation
  ```sql
  CREATE INDEX vectors_course_id_idx ON vectors(course_id);
  CREATE INDEX vectors_embedding_idx ON vectors USING ivfflat (embedding vector_cosine_ops);
  ```
- [ ] Configuration des politiques de sécurité
  ```sql
  ALTER TABLE vectors ENABLE ROW LEVEL SECURITY;
  CREATE POLICY "Vectors are viewable by authenticated users" ON vectors
    FOR SELECT USING (auth.role() = 'authenticated');
  ```

### 1.3 Tests et Configuration des APIs
- [ ] Test de l'API d'embeddings
  ```python
  from pathlib import Path
  import requests

  def test_embedding_api():
      test_query = "Test de connexion à l'API"
      response = requests.post(
          "https://lmspaul--llamaindex-embeddings-fast-api.modal.run/encode_queries",
          json={"queries": [test_query]}
      )
      assert response.status_code == 200
      print("Dimension des embeddings:", len(response.json()["embeddings"][0]))
  ```
- [ ] Configuration Gemini Flash
  ```python
  import google.generativeai as genai
  
  def setup_gemini():
      genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
      model = genai.GenerativeModel('gemini-pro-vision')
      return model
  ```

### 1.4 Mise en Place du Pipeline PDF
- [ ] Création de la classe de base pour l'extraction
  ```python
  class PDFProcessor:
      def __init__(self, pdf_path):
          self.pdf_path = pdf_path
          self.pages = []
          self.images = []
          self.formulas = []
          
      def extract_content(self):
          # Code d'extraction
          pass
          
      def extract_images(self):
          # Code d'extraction des images
          pass
          
      def detect_formulas(self):
          # Code de détection des formules
          pass
  ```

## PHASE 2 : Traitement du Contenu (2-3 semaines)

### 2.1 Système de Chunking
- [ ] Définition des classes de base
  ```python
  class Chunk:
      def __init__(self):
          self.text = ""
          self.images = []
          self.formulas = []
          self.metadata = {}
          self.page_number = 0
          self.section = ""
          
  class ChunkManager:
      def __init__(self):
          self.chunks = []
          self.max_tokens = 500
          self.overlap = 50
          
      def create_chunks(self, content):
          # Code de chunking
          pass
  ```

### 2.2 Système d'Embeddings
- [ ] Class pour gérer les embeddings
  ```python
  class EmbeddingManager:
      def __init__(self, api_url):
          self.api_url = api_url
          
      async def get_embeddings(self, chunks):
          # Code génération embeddings
          pass
          
      async def store_embeddings(self, embeddings):
          # Code stockage Supabase
          pass
  ```

### 2.3 Pipeline Multimodal
- [ ] Intégration vision
  ```python
  class VisionProcessor:
      def __init__(self, model):
          self.model = model
          
      def process_image(self, image):
          # Code traitement image
          pass
          
      def process_schema(self, schema):
          # Code traitement schéma électrique
          pass
  ```

## PHASE 3 : Système RAG et QA (2-3 semaines)

### 3.1 Implémentation RAG
- [ ] Classe principale RAG
  ```python
  class RAGSystem:
      def __init__(self):
          self.embedding_manager = EmbeddingManager()
          self.vision_processor = VisionProcessor()
          self.query_processor = QueryProcessor()
          
      async def process_query(self, query):
          # Code traitement requête
          pass
  ```

### 3.2 Query Rewriting
- [ ] Système de reformulation
  ```python
  class QueryRewriter:
      def __init__(self):
          self.templates = {
              "how": "Expliquer le fonctionnement de {}",
              "what": "Définir et décrire {}",
              "why": "Expliquer pourquoi {} et donner les raisons"
          }
          
      def rewrite_query(self, query):
          # Code reformulation
          pass
  ```

### 3.3 Système de Conversation
- [ ] Gestion des conversations
  ```python
  class ConversationManager:
      def __init__(self):
          self.conversations = {}
          self.max_history = 5
          
      def add_message(self, conversation_id, message):
          # Code gestion message
          pass
          
      def get_context(self, conversation_id):
          # Code récupération contexte
          pass
  ```

## PHASE 4 : Tests et Optimisation (1-2 semaines)

### 4.1 Tests
- [ ] Tests unitaires
  ```python
  def test_pdf_extraction():
      processor = PDFProcessor("test.pdf")
      content = processor.extract_content()
      assert len(content) > 0
      assert len(content.images) > 0
  ```

### 4.2 Cache Redis
- [ ] Configuration cache
  ```python
  class CacheManager:
      def __init__(self):
          self.redis_client = redis.Redis()
          self.ttl = 86400  # 24h
          
      def cache_embedding(self, key, embedding):
          # Code cache
          pass
  ```

### 4.3 Documentation
- [ ] Structure API
  ```python
  """
  POST /api/query
  {
      "query": string,
      "level": "ING1" | "ING2" | "ING3",
      "context": {...}
  }
  """
  ```

## Points de Contrôle et Livrables

### Phase 1
- [ ] Tests de connexion API réussis
- [ ] Extraction PDF fonctionnelle
- [ ] Base de données configurée

### Phase 2
- [ ] Chunks correctement générés
- [ ] Embeddings stockés
- [ ] Images traitées

### Phase 3
- [ ] RAG fonctionnel
- [ ] Conversations fluides
- [ ] Adaptation au niveau

### Phase 4
- [ ] Tests passants
- [ ] Performance optimale
- [ ] Documentation complète

## Notes Techniques
1. Taille recommandée des chunks : 500-700 tokens
2. Overlap entre chunks : 10-15%
3. Format des embeddings : vecteurs 1536D
4. Temps de réponse cible : < 2 secondes
5. Cache invalidation : 24h par défaut