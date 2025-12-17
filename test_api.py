"""
Script de test de l'API
"""
import requests
import json

base_url = "http://localhost:8000"

def test_endpoints():
    """Teste les endpoints de l'API"""
    print("=" * 50)
    print("Test des endpoints de l'API")
    print("=" * 50)
    
    # Test de la racine
    try:
        response = requests.get(f"{base_url}/")
        print(f"[OK] GET / : {response.status_code}")
        print(f"     {response.json()}")
    except Exception as e:
        print(f"[ERREUR] GET / : {e}")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"[OK] GET /health : {response.status_code}")
        print(f"     {response.json()}")
    except Exception as e:
        print(f"[ERREUR] GET /health : {e}")
    
    # Test clients
    try:
        response = requests.get(f"{base_url}/clients/")
        print(f"[OK] GET /clients/ : {response.status_code}")
        if response.status_code == 200:
            clients = response.json()
            print(f"     Nombre de clients: {len(clients)}")
        else:
            print(f"     Erreur: {response.text}")
    except Exception as e:
        print(f"[ERREUR] GET /clients/ : {e}")
        print(f"     Details: {str(e)}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_endpoints()

