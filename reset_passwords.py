"""Script pour réinitialiser les mots de passe des utilisateurs existants"""
from sqlalchemy import text
from database import SessionLocal
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_passwords():
    """Réinitialise les mots de passe avec un mot de passe par défaut"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Réinitialisation des mots de passe")
        print("=" * 60)
        print()
        print("⚠️  ATTENTION: Ce script va réinitialiser tous les mots de passe")
        print("   Les utilisateurs devront utiliser le mot de passe par défaut: 'azerty'")
        print()
        
        response = input("Voulez-vous continuer? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Annulé.")
            return
        
        # Mot de passe par défaut
        default_password = "azerty"
        hashed_password = pwd_context.hash(default_password)
        
        print()
        print(f"Hash du mot de passe par défaut: {hashed_password[:50]}...")
        print()
        
        # Obtenir tous les utilisateurs
        result = db.execute(text("""
            SELECT id, email 
            FROM utilisateurs
        """))
        
        users = result.fetchall()
        print(f"[INFO] {len(users)} utilisateur(s) à réinitialiser")
        print()
        
        for user in users:
            user_id, email = user
            print(f"  Réinitialisation pour {email} (ID: {user_id})...")
            
            # Mettre à jour le mot de passe
            db.execute(text("""
                UPDATE utilisateurs 
                SET password_hash = :hash
                WHERE id = :user_id
            """), {"hash": hashed_password, "user_id": user_id})
        
        db.commit()
        print()
        print(f"[SUCCÈS] {len(users)} mot(s) de passe réinitialisé(s)")
        print()
        print("Mot de passe par défaut pour tous les utilisateurs: 'azerty'")
        print("Les utilisateurs peuvent ensuite changer leur mot de passe dans l'application.")
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
    reset_passwords()


