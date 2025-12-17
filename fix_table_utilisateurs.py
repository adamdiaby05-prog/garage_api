"""Script pour vérifier et corriger la structure de la table utilisateurs"""
from sqlalchemy import inspect, text
from database import engine, SessionLocal
import sys

def check_and_fix_table():
    """Vérifie et corrige la structure de la table utilisateurs"""
    try:
        print("=" * 60)
        print("Vérification de la structure de la table 'utilisateurs'")
        print("=" * 60)
        print()
        
        inspector = inspect(engine)
        
        # Vérifier si la table existe
        tables = inspector.get_table_names()
        if 'utilisateurs' not in tables:
            print("[ERREUR] La table 'utilisateurs' n'existe pas!")
            print("Création de la table...")
            create_table()
            return
        
        print("[OK] La table 'utilisateurs' existe")
        print()
        
        # Obtenir les colonnes actuelles
        columns = inspector.get_columns('utilisateurs')
        column_names = [col['name'] for col in columns]
        
        print(f"Colonnes actuelles ({len(column_names)}):")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        print()
        
        # Colonnes attendues
        expected_columns = {
            'id': 'INTEGER',
            'nom_complet': 'VARCHAR(200)',
            'email': 'VARCHAR(150)',
            'password_hash': 'VARCHAR(255)',
            'role': 'ENUM',
            'telephone': 'VARCHAR(20)',
            'created_at': 'TIMESTAMP ou VARCHAR(50)'
        }
        
        missing_columns = []
        for col_name in expected_columns.keys():
            if col_name not in column_names:
                missing_columns.append(col_name)
                print(f"[MANQUANT] Colonne '{col_name}' n'existe pas")
        
        if missing_columns:
            print()
            print(f"[ACTION] {len(missing_columns)} colonne(s) manquante(s). Correction nécessaire...")
            
            # Créer les colonnes manquantes
            db = SessionLocal()
            try:
                for col_name in missing_columns:
                    if col_name == 'nom_complet':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN nom_complet VARCHAR(200) NOT NULL DEFAULT ''"))
                        print(f"[OK] Colonne 'nom_complet' ajoutée")
                    elif col_name == 'email':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN email VARCHAR(150) NOT NULL DEFAULT ''"))
                        db.execute(text("ALTER TABLE utilisateurs ADD UNIQUE KEY email (email)"))
                        print(f"[OK] Colonne 'email' ajoutée")
                    elif col_name == 'password_hash':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))
                        print(f"[OK] Colonne 'password_hash' ajoutée")
                    elif col_name == 'role':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN role ENUM('client','garage','admin') DEFAULT 'client'"))
                        print(f"[OK] Colonne 'role' ajoutée")
                    elif col_name == 'telephone':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN telephone VARCHAR(20) DEFAULT NULL"))
                        print(f"[OK] Colonne 'telephone' ajoutée")
                    elif col_name == 'created_at':
                        db.execute(text("ALTER TABLE utilisateurs ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"))
                        print(f"[OK] Colonne 'created_at' ajoutée")
                
                db.commit()
                print()
                print("[SUCCÈS] Table corrigée avec succès!")
                
            except Exception as e:
                db.rollback()
                print(f"[ERREUR] Impossible de corriger la table: {e}")
                print()
                print("Solution alternative: Supprimez et recréez la table")
                print("1. Connectez-vous à phpMyAdmin")
                print("2. Supprimez la table 'utilisateurs'")
                print("3. Exécutez le script create_users_table.sql")
                return
            finally:
                db.close()
        else:
            print("[OK] Toutes les colonnes nécessaires sont présentes!")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_table():
    """Crée la table utilisateurs si elle n'existe pas"""
    db = SessionLocal()
    try:
        create_sql = """
        CREATE TABLE IF NOT EXISTS `utilisateurs` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `nom_complet` varchar(200) NOT NULL,
          `email` varchar(150) NOT NULL,
          `password_hash` varchar(255) NOT NULL,
          `role` enum('client','garage','admin') DEFAULT 'client',
          `telephone` varchar(20) DEFAULT NULL,
          `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
          PRIMARY KEY (`id`),
          UNIQUE KEY `email` (`email`),
          KEY `idx_role` (`role`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        db.execute(text(create_sql))
        db.commit()
        print("[OK] Table 'utilisateurs' créée avec succès!")
    except Exception as e:
        db.rollback()
        print(f"[ERREUR] Impossible de créer la table: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_table()

