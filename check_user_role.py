"""
Script pour vérifier et corriger les rôles des utilisateurs dans la base de données
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def check_user_role(email: str):
    """Vérifie le rôle d'un utilisateur dans la base de données"""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Vérifier tous les utilisateurs avec cet email
        result = db.execute(
            text("SELECT id, email, role, garage_id, nom_complet FROM utilisateurs WHERE email = :email"),
            {"email": email}
        )
        users = result.fetchall()
        
        if not users:
            print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
            return
        
        print(f"\n📋 Utilisateurs trouvés avec l'email '{email}':")
        print("-" * 80)
        
        for user in users:
            user_id, user_email, role, garage_id, nom_complet = user
            print(f"ID: {user_id}")
            print(f"Email: {user_email}")
            print(f"Rôle: {role}")
            print(f"Garage ID: {garage_id}")
            print(f"Nom complet: {nom_complet}")
            print("-" * 80)
        
        if len(users) > 1:
            print(f"\n⚠️  ATTENTION: Il y a {len(users)} utilisateurs avec le même email!")
            print("Cela peut causer des problèmes de connexion.")
            print("\nVoulez-vous supprimer les doublons? (garder le plus récent)")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def fix_user_role(email: str, new_role: str):
    """Corrige le rôle d'un utilisateur"""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Vérifier les rôles valides
        valid_roles = ['client', 'garage', 'admin']
        if new_role not in valid_roles:
            print(f"❌ Rôle invalide. Rôles valides: {', '.join(valid_roles)}")
            return
        
        # Mettre à jour le rôle
        result = db.execute(
            text("UPDATE utilisateurs SET role = :role WHERE email = :email"),
            {"role": new_role, "email": email}
        )
        db.commit()
        
        if result.rowcount > 0:
            print(f"✅ Rôle mis à jour pour {email}: {new_role}")
        else:
            print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def remove_duplicates(email: str, keep_latest: bool = True):
    """Supprime les doublons d'utilisateurs avec le même email"""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Récupérer tous les utilisateurs avec cet email
        result = db.execute(
            text("SELECT id, email, role, created_at FROM utilisateurs WHERE email = :email ORDER BY created_at DESC"),
            {"email": email}
        )
        users = result.fetchall()
        
        if len(users) <= 1:
            print(f"✅ Aucun doublon trouvé pour {email}")
            return
        
        print(f"\n📋 {len(users)} utilisateurs trouvés avec l'email '{email}'")
        
        if keep_latest:
            # Garder le plus récent (premier dans la liste triée DESC)
            keep_id = users[0][0]
            delete_ids = [user[0] for user in users[1:]]
        else:
            # Garder le plus ancien
            keep_id = users[-1][0]
            delete_ids = [user[0] for user in users[:-1]]
        
        print(f"✅ Conservation de l'utilisateur ID: {keep_id}")
        print(f"🗑️  Suppression des utilisateurs ID: {delete_ids}")
        
        # Supprimer les doublons
        for user_id in delete_ids:
            db.execute(
                text("DELETE FROM utilisateurs WHERE id = :id"),
                {"id": user_id}
            )
        
        db.commit()
        print(f"✅ {len(delete_ids)} utilisateur(s) supprimé(s)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_user_role.py check <email>          # Vérifier le rôle")
        print("  python check_user_role.py fix <email> <role>     # Corriger le rôle")
        print("  python check_user_role.py remove-duplicates <email>  # Supprimer les doublons")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        if len(sys.argv) < 3:
            print("❌ Email requis")
            sys.exit(1)
        check_user_role(sys.argv[2])
    
    elif command == "fix":
        if len(sys.argv) < 4:
            print("❌ Email et rôle requis")
            sys.exit(1)
        fix_user_role(sys.argv[2], sys.argv[3])
    
    elif command == "remove-duplicates":
        if len(sys.argv) < 3:
            print("❌ Email requis")
            sys.exit(1)
        remove_duplicates(sys.argv[2])
    
    else:
        print(f"❌ Commande inconnue: {command}")



