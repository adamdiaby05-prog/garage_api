"""Script pour vérifier que l'API répond correctement"""
import requests
import sys

def test_api():
    """Test si l'API répond"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Vérification de l'API FastAPI")
    print("=" * 60)
    print()
    
    # Test 1: Endpoint root
    try:
        print(f"Test 1: GET {base_url}/")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"[OK] API répond (Status: {response.status_code})")
            print(f"     Réponse: {response.json()}")
        else:
            print(f"[ERREUR] Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERREUR] Impossible de se connecter à l'API")
        print("         Assurez-vous que l'API est démarrée avec: py main.py")
        return False
    except requests.exceptions.Timeout:
        print("[ERREUR] Timeout - L'API ne répond pas")
        return False
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False
    
    print()
    
    # Test 2: Endpoint health
    try:
        print(f"Test 2: GET {base_url}/health")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Health check réussi (Status: {response.status_code})")
            print(f"     Réponse: {response.json()}")
        else:
            print(f"[ERREUR] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False
    
    print()
    
    # Test 3: Documentation Swagger
    try:
        print(f"Test 3: GET {base_url}/docs")
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Documentation Swagger accessible")
        else:
            print(f"[INFO] Documentation non accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"[INFO] Documentation non accessible: {e}")
    
    print()
    print("=" * 60)
    print("[SUCCÈS] L'API fonctionne correctement!")
    print("=" * 60)
    print()
    print("Pour l'émulateur Android, utilisez: http://10.0.2.2:8000")
    print("Pour un appareil physique, utilisez l'IP de votre machine")
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)

