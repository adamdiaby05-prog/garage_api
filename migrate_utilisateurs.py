"""Script pour migrer les données existantes vers la nouvelle structure"""
from sqlalchemy import text
from database import SessionLocal
import sys

def migrate_data():
    """Migre les données de l'ancienne structure vers la nouvelle"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Migration des données de la table 'utilisateurs'")
        print("=" * 60)
        print()
        
        # Vérifier si des données existent avec l'ancienne structure
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM utilisateurs 
            WHERE (nom IS NOT NULL OR prenom IS NOT NULL) 
            AND (nom_complet IS NULL OR nom_complet = '')
        """))
        count = result.scalar()
        
        if count > 0:
            print(f"[INFO] {count} utilisateur(s) à migrer")
            print()
            
            # Mettre à jour nom_complet à partir de nom et prenom
            db.execute(text("""
                UPDATE utilisateurs 
                SET nom_complet = CONCAT(
                    COALESCE(nom, ''), 
                    ' ', 
                    COALESCE(prenom, '')
                )
                WHERE (nom IS NOT NULL OR prenom IS NOT NULL) 
                AND (nom_complet IS NULL OR nom_complet = '')
            """))
            
            # Mettre à jour password_hash à partir de mot_de_passe si nécessaire
            result = db.execute(text("""
                SELECT COUNT(*) as count 
                FROM utilisateurs 
                WHERE mot_de_passe IS NOT NULL 
                AND (password_hash IS NULL OR password_hash = '')
            """))
            count_pwd = result.scalar()
            
            if count_pwd > 0:
                print(f"[INFO] Migration de {count_pwd} mot(s) de passe")
                db.execute(text("""
                    UPDATE utilisateurs 
                    SET password_hash = mot_de_passe
                    WHERE mot_de_passe IS NOT NULL 
                    AND (password_hash IS NULL OR password_hash = '')
                """))
            
            db.commit()
            print("[OK] Données migrées avec succès!")
        else:
            print("[INFO] Aucune donnée à migrer")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"[ERREUR] Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()

