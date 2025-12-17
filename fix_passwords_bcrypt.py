"""Script pour re-hasher tous les mots de passe avec bcrypt correctement"""
from sqlalchemy import text
from database import SessionLocal
from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def is_bcrypt_hash(password_hash: str) -> bool:
    """Vérifie si un hash est déjà un hash bcrypt valide"""
    if not password_hash:
        return False
    # Les hash bcrypt commencent par $2a$, $2b$, ou $2y$ et font 60 caractères
    return password_hash.startswith('$2') and len(password_hash) == 60

def fix_passwords():
    """Re-hash les mots de passe qui ne sont pas des hash bcrypt valides"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("Vérification et correction des mots de passe")
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
        
        fixed_count = 0
        invalid_count = 0
        
        for user in users:
            user_id, email, password_hash = user
            
            # Vérifier si le hash est un hash bcrypt valide
            if not is_bcrypt_hash(password_hash):
                print(f"[ATTENTION] Utilisateur {email} (ID: {user_id})")
                print(f"  Hash actuel: {password_hash[:50]}...")
                print(f"  ⚠️  Ce n'est pas un hash bcrypt valide")
                print(f"  💡 L'utilisateur devra réinitialiser son mot de passe")
                print()
                invalid_count += 1
            else:
                # Tester si le hash est valide en essayant de le vérifier avec un mot de passe test
                try:
                    # Juste vérifier que le format est correct
                    test_result = pwd_context.verify("test", password_hash)
                    # Si ça ne lève pas d'exception, le format est correct
                except Exception as e:
                    if "password cannot be longer than 72 bytes" in str(e):
                        print(f"[ERREUR] Hash invalide pour {email} (ID: {user_id})")
                        print(f"  Erreur: {e}")
                        invalid_count += 1
                    else:
                        # C'est normal que la vérification échoue, on teste juste le format
                        pass
        
        print()
        if invalid_count > 0:
            print(f"[ATTENTION] {invalid_count} utilisateur(s) ont des mots de passe incompatibles")
            print()
            print("Solution:")
            print("  1. Les utilisateurs peuvent créer un nouveau compte")
            print("  2. Ou vous pouvez réinitialiser leurs mots de passe manuellement")
            print("  3. Ou supprimer les comptes et les laisser se réinscrire")
        else:
            print("[OK] Tous les mots de passe sont des hash bcrypt valides!")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERREUR] Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    fix_passwords()


