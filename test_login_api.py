"""Script pour tester l'endpoint de login"""
import requests
import json

def test_login():
    """Test l'endpoint de login"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Test de l'endpoint de login")
    print("=" * 60)
    print()
    
    # Test avec des identifiants de test
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        print(f"Test: POST {base_url}/auth/login")
        print(f"Données: {json.dumps(login_data, indent=2)}")
        print()
        
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Login réussi!")
            print(f"Token: {data.get('token', 'N/A')[:50]}...")
            print(f"User: {data.get('nom_complet', 'N/A')}")
            print(f"Role: {data.get('role', 'N/A')}")
        elif response.status_code == 401:
            print("[INFO] Email ou mot de passe incorrect (normal si l'utilisateur n'existe pas)")
            print(f"Réponse: {response.text}")
        elif response.status_code == 500:
            print("[ERREUR] Erreur serveur!")
            print(f"Réponse: {response.text}")
        else:
            print(f"[ATTENTION] Status code inattendu: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"[ERREUR] {e}")

if __name__ == "__main__":
    test_login()

