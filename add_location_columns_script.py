#!/usr/bin/env python3
"""
Script pour ajouter les colonnes de localisation aux tables demandes_prestations et garages
À exécuter dans le conteneur Docker de l'API
"""
import sys
from sqlalchemy import text
from database import engine
from config import settings

def add_location_columns():
    """Ajoute les colonnes de localisation aux tables"""
    try:
        with engine.connect() as connection:
            # Démarrer une transaction
            trans = connection.begin()
            
            try:
                print("🔄 Ajout des colonnes de localisation...")
                
                # Ajouter les colonnes à demandes_prestations
                print("   - Ajout de client_latitude et client_longitude à demandes_prestations...")
                try:
                    connection.execute(text("""
                        ALTER TABLE demandes_prestations 
                        ADD COLUMN client_latitude DECIMAL(10, 8) NULL
                    """))
                    print("   ✅ client_latitude ajoutée")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("   ⚠️  client_latitude existe déjà")
                    else:
                        raise
                
                try:
                    connection.execute(text("""
                        ALTER TABLE demandes_prestations 
                        ADD COLUMN client_longitude DECIMAL(11, 8) NULL
                    """))
                    print("   ✅ client_longitude ajoutée")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("   ⚠️  client_longitude existe déjà")
                    else:
                        raise
                
                # Ajouter les colonnes à garages
                print("   - Ajout de latitude et longitude à garages...")
                try:
                    connection.execute(text("""
                        ALTER TABLE garages 
                        ADD COLUMN latitude DECIMAL(10, 8) NULL
                    """))
                    print("   ✅ latitude ajoutée")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("   ⚠️  latitude existe déjà")
                    else:
                        raise
                
                try:
                    connection.execute(text("""
                        ALTER TABLE garages 
                        ADD COLUMN longitude DECIMAL(11, 8) NULL
                    """))
                    print("   ✅ longitude ajoutée")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("   ⚠️  longitude existe déjà")
                    else:
                        raise
                
                # Créer les index
                print("   - Création des index...")
                try:
                    connection.execute(text("""
                        CREATE INDEX idx_demandes_client_location 
                        ON demandes_prestations(client_latitude, client_longitude)
                    """))
                    print("   ✅ Index idx_demandes_client_location créé")
                except Exception as e:
                    if "Duplicate key name" in str(e) or "already exists" in str(e):
                        print("   ⚠️  Index idx_demandes_client_location existe déjà")
                    else:
                        raise
                
                try:
                    connection.execute(text("""
                        CREATE INDEX idx_garages_location 
                        ON garages(latitude, longitude)
                    """))
                    print("   ✅ Index idx_garages_location créé")
                except Exception as e:
                    if "Duplicate key name" in str(e) or "already exists" in str(e):
                        print("   ⚠️  Index idx_garages_location existe déjà")
                    else:
                        raise
                
                # Commit la transaction
                trans.commit()
                print("\n✅ Toutes les colonnes et index ont été ajoutés avec succès!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Erreur lors de l'ajout des colonnes: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        print(f"   Host: {settings.DB_HOST}")
        print(f"   Database: {settings.DB_NAME}")
        return False

if __name__ == "__main__":
    print("🚀 Début de l'ajout des colonnes de localisation...")
    print(f"📍 Connexion à: {settings.DB_HOST}/{settings.DB_NAME}")
    print()
    
    success = add_location_columns()
    
    sys.exit(0 if success else 1)

