# test_direct_api.py
import requests
import json

def test_direct_api():
    base_url = "https://lmspaul--llamaindex-embeddings-fast-api.modal.run"
    
    # Test avec le format exact du README original
    url = f"{base_url}/encode_queries"
    payload = {
        "queries": ["Ceci est un test sur les capteurs en électronique"]
    }
    
    print("Sending payload:", json.dumps(payload))
    
    response = requests.post(url, json=payload, params={"dimension": 1536})
    
    print("Status code:", response.status_code)
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(f"Embeddings count: {len(data['embeddings'])}")
        print(f"Embedding dimension: {len(data['embeddings'][0])}")
    else:
        print("Error response:", response.text)

if __name__ == "__main__":
    test_direct_api()