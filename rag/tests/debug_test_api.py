# tests/debug_test_api.py
import requests
import json
import os
from dotenv import load_dotenv
import traceback

# Charger les variables d'environnement
load_dotenv()

# URL de base de l'API
BASE_URL = "http://localhost:8000"

def test_health():
    """Teste l'endpoint de health check."""
    print("\n=== Test Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status code: {response.status_code}")
        data = response.json()
        print(f"Response data: {data}")
        assert response.status_code == 200
        assert data["status"] == "healthy"
        print("✅ Test health check réussi")
    except Exception as e:
        print(f"❌ Test health check échoué: {str(e)}")
        traceback.print_exc()

def test_models():
    """Teste la récupération des modèles disponibles."""
    print("\n=== Test Modèles ===")
    try:
        response = requests.get(f"{BASE_URL}/queries/models")
        print(f"Status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        data = response.json()
        print(f"Response data type: {type(data)}")
        print(f"Response data: {data}")
        assert isinstance(data, list)
        if len(data) > 0:
            print(f"Modèles disponibles: {len(data)}")
            print(f"Premier modèle: {data[0].get('id', 'N/A')}")
        print("✅ Test récupération des modèles réussi")
    except Exception as e:
        print(f"❌ Test récupération des modèles échoué: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Exécution des tests de debug de l'API Max RAG Multimodal...")
    
    test_health()
    test_models()