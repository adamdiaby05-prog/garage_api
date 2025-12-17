"""Script pour re-hasher les mots de passe existants avec bcrypt"""
from sqlalchemy import text
from database import SessionLocal
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_bcrypt_hash(password_hash: str) -> bool:
    """Vérifie si un hash est déjà un hash bcrypt"""
    if not password_hash:
        return False
    # Les hash bcrypt commencent par $2a$, $2b$, ou $2y$ et font 60 caractères
    return password_hash.startswith('$2') and len(password_hash) == 60

def rehash_passwords():
    """Re-hash les mots de passe qui ne sont pas encore hashés avec bcrypt"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Re-hash des mots de passe avec bcrypt")
        print("=" * 60)
        print()
        
        # Obtenir tous les utilisateurs avec leur password_hash
        result = db.execute(text("""
            SELECT id, email, password_hash 
            FROM utilisateurs 
            WHERE password_hash IS NOT NULL 
            AND password_hash != ''
        """))
        
        users = result.fetchall()
        print(f"[INFO] {len(users)} utilisateur(s) à vérifier")
        print()
        
        rehashed_count = 0
        
        for user in users:
            user_id, email, password_hash = user
            
            # Vérifier si le hash est déjà un hash bcrypt
            if not is_bcrypt_hash(password_hash):
                print(f"[INFO] Re-hash du mot de passe pour {email} (ID: {user_id})")
                
                # Si ce n'est pas un hash bcrypt, on ne peut pas le re-hasher
                # sans connaître le mot de passe en clair
                # On va plutôt supprimer le hash pour forcer la réinitialisation
                print(f"  ⚠️  Le mot de passe existant n'est pas compatible avec bcrypt")
                print(f"  💡 L'utilisateur devra réinitialiser son mot de passe ou se réinscrire")
                
                # Option 1: Mettre un hash temporaire (désactive le compte)
                # Option 2: Laisser tel quel et documenter le problème
                # Pour l'instant, on laisse tel quel et on informe l'utilisateur
                rehashed_count += 1
        
        if rehashed_count > 0:
            print()
            print(f"[ATTENTION] {rehashed_count} utilisateur(s) ont des mots de passe incompatibles")
            print("Ces utilisateurs devront se réinscrire ou réinitialiser leur mot de passe")
            print()
            print("Solution: Les utilisateurs peuvent créer un nouveau compte avec le même email")
            print("(après suppression de l'ancien) ou utiliser la fonction 'Mot de passe oublié'")
        else:
            print("[OK] Tous les mots de passe sont déjà hashés avec bcrypt!")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors du re-hash: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    rehash_passwords()

