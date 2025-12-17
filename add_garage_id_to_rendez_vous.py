"""Script pour ajouter la colonne garage_id à la table rendez_vous"""
from sqlalchemy import text
from database import SessionLocal
import sys

def add_garage_id_column():
    """Ajoute la colonne garage_id à la table rendez_vous"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Ajout de la colonne garage_id à la table rendez_vous")
        print("=" * 60)
        print()
        
        # Vérifier si la colonne existe déjà
        result = db.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'garage_db'
            AND TABLE_NAME = 'rendez_vous'
            AND COLUMN_NAME = 'garage_id'
        """))
        count = result.scalar()
        
        if count > 0:
            print("[INFO] La colonne 'garage_id' existe déjà")
        else:
            print("[ACTION] Ajout de la colonne 'garage_id'...")
            db.execute(text("""
                ALTER TABLE rendez_vous 
                ADD COLUMN garage_id INT NULL,
                ADD FOREIGN KEY (garage_id) REFERENCES garages(id) ON DELETE SET NULL
            """))
            db.commit()
            print("[OK] Colonne 'garage_id' ajoutée avec succès!")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"[ERREUR] Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    add_garage_id_column()


