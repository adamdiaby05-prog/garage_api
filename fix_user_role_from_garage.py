"""
Script pour corriger le rôle des utilisateurs en fonction des garages existants
Si un garage existe avec l'email d'un utilisateur, l'utilisateur DOIT être un garage
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings

def fix_user_roles_from_garages():
    """Corrige les rôles des utilisateurs en fonction des garages existants"""
    try:
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Récupérer tous les garages
        result_garages = db.execute(
            text("SELECT id, email, nom_garage FROM garages WHERE email IS NOT NULL AND email != ''")
        )
        garages = result_garages.fetchall()
        
        print(f"📋 {len(garages)} garage(s) trouvé(s) avec un email")
        print("=" * 80)
        
        corrections = 0
        
        for garage in garages:
            garage_id, garage_email, nom_garage = garage
            print(f"\n🔍 Vérification du garage: {nom_garage} (ID: {garage_id}, Email: {garage_email})")
            
            # Chercher l'utilisateur avec cet email
            result_user = db.execute(
                text("SELECT id, email, role, garage_id, nom_complet FROM utilisateurs WHERE email = :email"),
                {"email": garage_email}
            )
            users = result_user.fetchall()
            
            if not users:
                print(f"   ⚠️  Aucun utilisateur trouvé avec l'email {garage_email}")
                continue
            
            if len(users) > 1:
                print(f"   ⚠️  {len(users)} utilisateurs trouvés avec le même email, utilisation du plus récent")
            
            user = users[0]
            user_id, user_email, user_role, user_garage_id, nom_complet = user
            
            print(f"   👤 Utilisateur: {nom_complet} (ID: {user_id})")
            print(f"      Rôle actuel: {user_role}")
            print(f"      Garage ID actuel: {user_garage_id}")
            
            # Vérifier si une correction est nécessaire
            needs_fix = False
            if user_role != 'garage':
                print(f"      ❌ Rôle incorrect: '{user_role}' devrait être 'garage'")
                needs_fix = True
            
            if user_garage_id != garage_id:
                print(f"      ❌ Garage ID incorrect: {user_garage_id} devrait être {garage_id}")
                needs_fix = True
            
            if needs_fix:
                # Corriger
                db.execute(
                    text("UPDATE utilisateurs SET role = 'garage', garage_id = :garage_id WHERE id = :user_id"),
                    {"garage_id": garage_id, "user_id": user_id}
                )
                db.commit()
                print(f"      ✅ Corrigé: rôle='garage', garage_id={garage_id}")
                corrections += 1
            else:
                print(f"      ✅ Déjà correct")
        
        print("\n" + "=" * 80)
        print(f"✅ {corrections} correction(s) effectuée(s)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Correction des rôles utilisateurs en fonction des garages")
    print("=" * 80)
    fix_user_roles_from_garages()



