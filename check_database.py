"""Script pour vérifier et créer la table utilisateurs si nécessaire"""
from database import engine, Base
from models_auth import Utilisateur
import sys

def check_and_create_table():
    """Vérifie et crée la table utilisateurs si elle n'existe pas"""
    try:
        print("Vérification de la connexion à la base de données...")
        
        # Créer toutes les tables définies dans les modèles
        Base.metadata.create_all(bind=engine)
        
        print("[OK] Tables créées/vérifiées avec succès")
        print("[OK] La table 'utilisateurs' devrait maintenant exister")
        
        # Vérifier que la table existe en essayant une requête simple
        from sqlalchemy.orm import Session
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            count = db.query(Utilisateur).count()
            print(f"[OK] La table 'utilisateurs' existe et contient {count} utilisateur(s)")
        except Exception as e:
            print(f"[ERREUR] Problème lors de la vérification: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERREUR] Impossible de créer/vérifier les tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_and_create_table()

