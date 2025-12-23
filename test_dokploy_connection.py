"""
Script pour tester la connexion à la base de données Dokploy
"""
from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_connection():
    """Teste la connexion à la base de données"""
    print("=" * 80)
    print("🔍 Test de connexion à la base de données")
    print("=" * 80)
    
    # Afficher la configuration
    print(f"\n📋 Configuration actuelle:")
    print(f"   Host: {settings.DB_HOST}")
    print(f"   Port: {settings.DB_PORT}")
    print(f"   User: {settings.DB_USER}")
    print(f"   Database: {settings.DB_NAME}")
    print(f"   Password: {'*' * len(settings.DB_PASSWORD) if settings.DB_PASSWORD else '(vide)'}")
    print(f"\n   URL de connexion: {settings.database_url.replace(settings.DB_PASSWORD, '***')}")
    
    try:
        # Créer le moteur
        print(f"\n🔌 Tentative de connexion...")
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        # Tester la connexion
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("   ✅ Connexion réussie!")
        
        # Vérifier si la base de données existe
        print(f"\n📊 Vérification de la base de données '{settings.DB_NAME}'...")
        Session = sessionmaker(bind=engine)
        db = Session()
        
        try:
            result = db.execute(text(f"USE {settings.DB_NAME}"))
            print(f"   ✅ Base de données '{settings.DB_NAME}' accessible")
        except Exception as e:
            print(f"   ⚠️  Base de données '{settings.DB_NAME}' non trouvée: {e}")
            print(f"   💡 Créez la base avec: CREATE DATABASE {settings.DB_NAME};")
        
        # Vérifier les tables
        print(f"\n📋 Tables disponibles:")
        result = db.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        
        if tables:
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("   ⚠️  Aucune table trouvée")
            print("   💡 Les tables seront créées automatiquement au premier démarrage de l'API")
        
        # Vérifier la table utilisateurs si elle existe
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = :db_name 
            AND table_name = 'utilisateurs'
        """), {"db_name": settings.DB_NAME})
        
        has_users_table = result.fetchone()[0] > 0
        
        if has_users_table:
            print(f"\n👥 Table 'utilisateurs' trouvée")
            result = db.execute(text("SELECT COUNT(*) FROM utilisateurs"))
            count = result.fetchone()[0]
            print(f"   Nombre d'utilisateurs: {count}")
            
            # Afficher quelques utilisateurs
            if count > 0:
                result = db.execute(text("SELECT id, email, role, garage_id FROM utilisateurs LIMIT 5"))
                users = result.fetchall()
                print(f"\n   Exemples d'utilisateurs:")
                for user in users:
                    user_id, email, role, garage_id = user
                    print(f"   - ID {user_id}: {email} (rôle: {role}, garage_id: {garage_id})")
        else:
            print(f"\n👥 Table 'utilisateurs' non trouvée")
            print("   💡 Exécutez create_users_table.sql pour la créer")
        
        db.close()
        
        print("\n" + "=" * 80)
        print("✅ Test terminé avec succès!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Erreur de connexion: {e}")
        print("\n💡 Vérifiez:")
        print("   1. Que les variables d'environnement sont correctement configurées")
        print("   2. Que la base de données Dokploy est accessible")
        print("   3. Que le host 'garage-database-8te5zx' est accessible depuis le conteneur API")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()



