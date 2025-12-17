"""Script pour tester directement le login avec un utilisateur"""
import requests
import json

def test_login():
    """Test l'endpoint de login avec différents utilisateurs"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Test de l'endpoint de login")
    print("=" * 60)
    print()
    
    # Liste des utilisateurs à tester
    test_users = [
        {"email": "a@gmail.com", "password": "azerty"},
        {"email": "b@gmail.com", "password": "azerty"},
        {"email": "test@example.com", "password": "azerty"},
    ]
    
    for user_data in test_users:
        print(f"Test avec: {user_data['email']}")
        print(f"Mot de passe: {user_data['password']}")
        print()
        
        try:
            response = requests.post(
                f"{base_url}/auth/login",
                json=user_data,
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] Login réussi!")
                print(f"  Token: {data.get('token', 'N/A')[:50]}...")
                print(f"  User: {data.get('nom_complet', 'N/A')}")
                print(f"  Role: {data.get('role', 'N/A')}")
            elif response.status_code == 401:
                print("[INFO] Email ou mot de passe incorrect")
            elif response.status_code == 500:
                print("[ERREUR] Erreur serveur!")
                try:
                    error_data = response.json()
                    print(f"  Détail: {error_data.get('detail', 'N/A')}")
                except:
                    print(f"  Réponse: {response.text[:200]}")
            else:
                print(f"[ATTENTION] Status code: {response.status_code}")
                print(f"  Réponse: {response.text[:200]}")
            
        except Exception as e:
            print(f"[ERREUR] {e}")
        
        print()
        print("-" * 60)
        print()

if __name__ == "__main__":
    test_login()


