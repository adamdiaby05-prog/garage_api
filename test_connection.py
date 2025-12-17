"""
Script de test de connexion a la base de donnees
"""
from database import engine, SessionLocal
from sqlalchemy import text
from config import settings

def test_connection():
    """Teste la connexion a la base de donnees"""
    print("=" * 50)
    print("Test de connexion a la base de donnees")
    print("=" * 50)
    print(f"Host: {settings.DB_HOST}")
    print(f"Port: {settings.DB_PORT}")
    print(f"Database: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")
    print("-" * 50)
    
    try:
        # Test de connexion
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("[OK] Connexion reussie!")
            
            # Verifier les tables
            print("\nVerification des tables...")
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"[OK] {len(tables)} table(s) trouvee(s):")
                for table in tables[:10]:  # Afficher les 10 premieres
                    print(f"  - {table}")
                if len(tables) > 10:
                    print(f"  ... et {len(tables) - 10} autre(s)")
            else:
                print("[WARNING] Aucune table trouvee")
            
            # Test d'une requete simple
            print("\nTest d'une requete...")
            try:
                result = connection.execute(text("SELECT COUNT(*) FROM clients"))
                count = result.scalar()
                print(f"[OK] Nombre de clients: {count}")
            except Exception as e:
                print(f"[WARNING] Erreur lors de la requete: {e}")
            
    except Exception as e:
        print(f"[ERREUR] Erreur de connexion: {e}")
        print("\nVerifiez:")
        print("  1. Que MySQL/MariaDB est demarre")
        print("  2. Que la base de donnees 'garage_db' existe")
        print("  3. Que les identifiants dans .env sont corrects")
        return False
    
    print("\n" + "=" * 50)
    print("Test termine!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_connection()

