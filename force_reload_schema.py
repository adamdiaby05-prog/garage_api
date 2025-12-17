"""Script pour forcer SQLAlchemy à recharger le schéma de la table"""
from sqlalchemy import text, MetaData, Table, inspect
from database import engine, Base
from models_auth import Utilisateur
import sys

def force_reload_schema():
    """Force SQLAlchemy à recharger le schéma"""
    try:
        print("=" * 60)
        print("Rechargement du schéma de la table utilisateurs")
        print("=" * 60)
        print()
        
        # Vérifier les colonnes directement dans la base de données
        inspector = inspect(engine)
        columns = inspector.get_columns('utilisateurs')
        column_names = [col['name'] for col in columns]
        
        print("Colonnes dans la base de données:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        print()
        
        # Vérifier que nom_complet existe
        if 'nom_complet' not in column_names:
            print("[ERREUR] La colonne 'nom_complet' n'existe toujours pas!")
            print("Exécutez: py fix_table_utilisateurs.py")
            return False
        
        # Vérifier que password_hash existe
        if 'password_hash' not in column_names:
            print("[ERREUR] La colonne 'password_hash' n'existe toujours pas!")
            print("Exécutez: py fix_table_utilisateurs.py")
            return False
        
        print("[OK] Toutes les colonnes nécessaires sont présentes")
        print()
        
        # Tester une requête directe
        from sqlalchemy.orm import Session
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            # Test avec une requête SQL directe
            result = db.execute(text("SELECT id, nom_complet, email, password_hash, role FROM utilisateurs LIMIT 1"))
            row = result.fetchone()
            
            if row:
                print("[OK] Requête SQL directe réussie")
                print(f"  Exemple: ID={row[0]}, nom_complet={row[1]}, email={row[2]}")
            else:
                print("[INFO] Aucun utilisateur dans la table")
            
            # Test avec SQLAlchemy ORM
            user = db.query(Utilisateur).first()
            if user:
                print("[OK] Requête SQLAlchemy ORM réussie")
                print(f"  Exemple: ID={user.id}, nom_complet={user.nom_complet}, email={user.email}")
            else:
                print("[INFO] Aucun utilisateur dans la table")
            
            print()
            print("[SUCCÈS] Le schéma est correct et accessible!")
            print()
            print("Si l'API affiche encore l'erreur, redémarrez l'API:")
            print("  1. Arrêtez l'API (Ctrl+C)")
            print("  2. Relancez: py main.py")
            
        except Exception as e:
            print(f"[ERREUR] Erreur lors du test: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = force_reload_schema()
    sys.exit(0 if success else 1)


