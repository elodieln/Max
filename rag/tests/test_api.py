# tests/test_api.py
import requests
import json
import os
from dotenv import load_dotenv
import time
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

# URL de base de l'API
BASE_URL = "http://localhost:8000"

def test_health():
    """Teste l'endpoint de health check."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Test health check réussi")

def test_models():
    """Teste la récupération des modèles disponibles."""
    response = requests.get(f"{BASE_URL}/queries/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        print(f"Modèles disponibles: {len(data)}")
        print(f"Premier modèle: {data[0].get('id', 'N/A')}")
    print("✅ Test récupération des modèles réussi")

def test_query():
    """Teste une requête simple."""
    payload = {
        "query": "Qu'est-ce qu'un condensateur?",
        "query_type": "question",
        "temperature": 0.5
    }
    response = requests.post(f"{BASE_URL}/queries/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "processing_time" in data
    print(f"⏱️ Temps de traitement: {data['processing_time']:.2f} secondes")
    print(f"🤖 Modèle utilisé: {data.get('model_used', 'N/A')}")
    print("✅ Test requête simple réussi")

def test_courses():
    """Teste la récupération des cours."""
    response = requests.get(f"{BASE_URL}/documents/courses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"Nombre de cours disponibles: {len(data)}")
    if len(data) > 0:
        print(f"Premier cours: {data[0].get('name', 'N/A')}")
    print("✅ Test récupération des cours réussi")

def test_embedding_stats():
    """Teste la récupération des statistiques d'embeddings."""
    response = requests.get(f"{BASE_URL}/embeddings/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_embeddings" in data
    print(f"Nombre total d'embeddings: {data['total_embeddings']}")
    print("✅ Test statistiques d'embeddings réussi")

def test_embedding_search():
    """Teste la recherche par embeddings."""
    payload = {
        "query": "Qu'est-ce qu'un condensateur?",
        "top_k": 3,
        "threshold": 0.5
    }
    response = requests.post(f"{BASE_URL}/embeddings/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    print(f"Nombre de résultats trouvés: {data['count']}")
    if data['count'] > 0:
        print(f"Premier résultat: Page {data['results'][0].get('page_number', 'N/A')} du cours {data['results'][0].get('courses', {}).get('name', 'N/A')}")
        print(f"Score de similarité: {data['results'][0].get('similarity', 'N/A')}")
    print("✅ Test recherche par embeddings réussi")

def test_document_upload():
    """Teste l'upload et le traitement d'un document."""
    # Chercher un fichier PDF de test
    test_pdf_path = None
    for path in ["tests/test.pdf", "data/test.pdf", "test.pdf"]:
        if os.path.exists(path):
            test_pdf_path = path
            break
    
    if not test_pdf_path:
        print("❌ Aucun fichier PDF de test trouvé, test ignoré")
        return
    
    # Préparer les données
    files = {
        'file': open(test_pdf_path, 'rb')
    }
    data = {
        'course_name': 'Test API Upload',
        'year': 'ING1'
    }
    
    # Envoyer la requête
    try:
        response = requests.post(f"{BASE_URL}/documents/process", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        print(f"Document traité: {result['message']}")
        print(f"ID du cours: {result['course_id']}")
        print("✅ Test upload de document réussi")
    except Exception as e:
        print(f"❌ Erreur lors du test d'upload: {str(e)}")
    finally:
        # Fermer le fichier
        files['file'].close()

def run_all_tests():
    """Execute tous les tests."""
    print("🧪 Exécution des tests de l'API Max RAG Multimodal...")
    
    try:
        test_health()
        test_models()
        test_courses()
        test_embedding_stats()
        test_embedding_search()
        test_query()
        test_document_upload()
        
        print("\n🎉 Tous les tests ont réussi!")
        
    except Exception as e:
        print(f"\n❌ Échec des tests: {str(e)}")

if __name__ == "__main__":
    run_all_tests()