from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from config import settings
import time

# Création du moteur de base de données avec meilleure gestion des erreurs
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_recycle=300,     # Recycle les connexions après 5 minutes
    pool_size=5,          # Nombre de connexions dans le pool
    max_overflow=10,      # Nombre maximum de connexions supplémentaires
    echo=settings.DEBUG,
    connect_args={
        "connect_timeout": 10,  # Timeout de connexion de 10 secondes
        "charset": "utf8mb4"
    }
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def test_connection(max_retries=3, retry_delay=2):
    """Teste la connexion à la base de données avec retry"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            print("✅ Connexion à la base de données réussie")
            return True
        except OperationalError as e:
            print(f"❌ Tentative {attempt + 1}/{max_retries} - Erreur de connexion: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Nouvelle tentative dans {retry_delay} secondes...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Impossible de se connecter à la base de données après {max_retries} tentatives")
                print(f"   URL: {settings.database_url.replace(settings.DB_PASSWORD, '***')}")
                return False
        except Exception as e:
            print(f"❌ Erreur inattendue lors de la connexion: {e}")
            return False
    return False


# Tester la connexion au démarrage
print("🔄 Test de connexion à la base de données...")
if not test_connection():
    print("⚠️  L'API démarrera mais la connexion à la base de données pourrait échouer")
    print("   Vérifiez les variables d'environnement dans Dokploy")


def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"❌ Erreur SQLAlchemy: {e}")
        db.rollback()
        raise
    finally:
        db.close()

