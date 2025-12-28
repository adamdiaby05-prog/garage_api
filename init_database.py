"""
Script d'initialisation de la base de données
Crée la base de données si elle n'existe pas et vérifie les permissions
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from config import settings
from urllib.parse import quote_plus

def create_database_if_not_exists():
    """Crée la base de données si elle n'existe pas"""
    # URL de connexion sans spécifier la base de données
    password_encoded = quote_plus(settings.DB_PASSWORD)
    base_url = f"mysql+pymysql://{settings.DB_USER}:{password_encoded}@{settings.DB_HOST}:{settings.DB_PORT}/"
    
    try:
        # Se connecter sans spécifier la base de données
        engine = create_engine(
            base_url,
            connect_args={"connect_timeout": 10, "charset": "utf8mb4"}
        )
        
        with engine.connect() as connection:
            # Créer la base de données si elle n'existe pas
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            connection.commit()
            print(f"✅ Base de données '{settings.DB_NAME}' créée ou déjà existante")
            
            # Vérifier les permissions (nécessite les privilèges root)
            try:
                connection.execute(text(f"GRANT ALL PRIVILEGES ON {settings.DB_NAME}.* TO '{settings.DB_USER}'@'%'"))
                connection.execute(text("FLUSH PRIVILEGES"))
                print(f"✅ Permissions accordées à l'utilisateur '{settings.DB_USER}'")
            except ProgrammingError as e:
                print(f"⚠️  Impossible d'accorder les permissions (nécessite root): {e}")
                print("   Assurez-vous que l'utilisateur a les permissions nécessaires")
            
            return True
            
    except OperationalError as e:
        print(f"❌ Erreur de connexion: {e}")
        print(f"   Host: {settings.DB_HOST}")
        print(f"   Port: {settings.DB_PORT}")
        print(f"   User: {settings.DB_USER}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_connection():
    """Teste la connexion à la base de données"""
    from database import test_connection as db_test
    return db_test()

if __name__ == "__main__":
    print("🔄 Initialisation de la base de données...")
    print(f"   Host: {settings.DB_HOST}")
    print(f"   Database: {settings.DB_NAME}")
    print(f"   User: {settings.DB_USER}")
    
    if create_database_if_not_exists():
        print("\n🔄 Test de connexion...")
        if test_connection():
            print("\n✅ Initialisation terminée avec succès!")
            sys.exit(0)
        else:
            print("\n❌ La base de données existe mais la connexion échoue")
            sys.exit(1)
    else:
        print("\n❌ Impossible de créer la base de données")
        sys.exit(1)


