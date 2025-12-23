"""
Script pour vérifier l'utilisateur a@gmail.com dans la base de données
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def check_user():
    """Vérifie l'utilisateur a@gmail.com dans la base de données"""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Vérifier l'utilisateur
        result = db.execute(
            text("""
                SELECT id, email, role, garage_id, nom_complet, created_at 
                FROM utilisateurs 
                WHERE email = :email
                ORDER BY id DESC
            """),
            {"email": "a@gmail.com"}
        )
        users = result.fetchall()
        
        if not users:
            print("❌ Aucun utilisateur trouvé avec l'email: a@gmail.com")
            return
        
        print(f"\n📋 Utilisateur(s) trouvé(s) avec l'email 'a@gmail.com':")
        print("=" * 80)
        
        for user in users:
            user_id, email, role, garage_id, nom_complet, created_at = user
            print(f"ID: {user_id}")
            print(f"Email: {email}")
            print(f"Rôle: {role}")
            print(f"Garage ID: {garage_id}")
            print(f"Nom complet: {nom_complet}")
            print(f"Créé le: {created_at}")
            print("-" * 80)
        
        if len(users) > 1:
            print(f"\n⚠️  ATTENTION: Il y a {len(users)} utilisateurs avec le même email!")
            print("Cela peut causer des problèmes. Le plus récent sera utilisé par l'API.")
        
        # Vérifier si un garage existe avec cet email
        result_garage = db.execute(
            text("""
                SELECT id, nom_garage, email 
                FROM garages 
                WHERE email = :email
            """),
            {"email": "a@gmail.com"}
        )
        garages = result_garage.fetchall()
        
        if garages:
            print(f"\n📋 Garage(s) trouvé(s) avec l'email 'a@gmail.com':")
            print("=" * 80)
            for garage in garages:
                garage_id, nom_garage, email = garage
                print(f"ID Garage: {garage_id}")
                print(f"Nom: {nom_garage}")
                print(f"Email: {email}")
                print("-" * 80)
        
        # Recommandation
        print("\n💡 Recommandation:")
        if users:
            user = users[0]
            user_id, email, role, garage_id, nom_complet, created_at = user
            
            if garage_id and role != 'garage':
                print("   → L'utilisateur a un garage_id mais le rôle n'est pas 'garage'")
                print("   → L'API corrigera automatiquement le rôle en 'garage' lors de la connexion")
            elif not garage_id and role == 'garage':
                print("   → L'utilisateur a le rôle 'garage' mais pas de garage_id")
                if garages:
                    print(f"   → Un garage existe avec cet email (ID: {garages[0][0]})")
                    print("   → L'API liera automatiquement le garage lors de la connexion")
                else:
                    print("   → Aucun garage trouvé avec cet email")
            elif not garage_id and role == 'client':
                print("   → L'utilisateur est un client (pas de garage_id)")
                print("   → C'est normal, l'API retournera le rôle 'client'")
            else:
                print("   → Configuration cohérente")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_user()



