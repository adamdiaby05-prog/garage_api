from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from typing import Optional
from database import get_db
from models_auth import Utilisateur, RoleEnum

router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 jours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Schémas
class UserRegister(BaseModel):
    nom_complet: str
    email: EmailStr
    password: str
    role: Optional[str] = "client"
    telephone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nom_complet: str
    email: str
    role: str
    telephone: Optional[str] = None
    garage_id: Optional[int] = None
    token: Optional[str] = None

    class Config:
        from_attributes = True


# Fonctions utilitaires
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    try:
        # Vérifier que le hash est valide
        if not hashed_password or len(hashed_password) < 10:
            return False
        
        # Utiliser directement bcrypt au lieu de passlib pour éviter les problèmes de compatibilité
        try:
            # Convertir le hash en bytes si c'est une string
            if isinstance(hashed_password, str):
                hash_bytes = hashed_password.encode('utf-8')
            else:
                hash_bytes = hashed_password
            
            # Convertir le mot de passe en bytes
            if isinstance(plain_password, str):
                password_bytes = plain_password.encode('utf-8')
            else:
                password_bytes = plain_password
            
            # Tronquer le mot de passe à 72 bytes (limite bcrypt)
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # Vérifier avec bcrypt directement
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except (ValueError, TypeError) as e:
            # Si bcrypt échoue, essayer avec passlib en dernier recours
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception as e2:
                print(f"Erreur de vérification (bcrypt et passlib): {e}, {e2}")
                return False
    except Exception as e:
        error_str = str(e)
        print(f"Erreur lors de la vérification du mot de passe: {error_str}")
        return False


def get_password_hash(password: str) -> str:
    """Hash un mot de passe"""
    # Convertir en bytes
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Tronquer le mot de passe à 72 bytes (limite bcrypt)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Utiliser bcrypt directement pour éviter les problèmes de compatibilité
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par email"""
    try:
        return db.query(Utilisateur).filter(Utilisateur.email == email).first()
    except Exception as e:
        error_str = str(e)
        print(f"Erreur lors de la récupération de l'utilisateur: {error_str}")
        # Si c'est une erreur de connexion à la base de données, la propager
        if "Can't connect to MySQL" in error_str or "Connection refused" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service de base de données indisponible. Vérifiez que MySQL/XAMPP est démarré."
            )
        raise


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Valider le rôle
    if user_data.role not in [r.value for r in RoleEnum]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rôle invalide. Rôles disponibles: client, garage, admin"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user_data.password)
    
    # Séparer nom et prénom si possible
    nom_parts = user_data.nom_complet.split(" ", 1)
    nom = nom_parts[0]
    prenom = nom_parts[1] if len(nom_parts) > 1 else None
    
    new_user = Utilisateur(
        nom_complet=user_data.nom_complet,
        email=user_data.email,
        password_hash=hashed_password,
        role=RoleEnum(user_data.role),
        telephone=user_data.telephone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Créer un token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role.value},
        expires_delta=access_token_expires
    )
    
    return UserResponse(
        id=new_user.id,
        nom_complet=new_user.nom_complet,
        email=new_user.email,
        role=new_user.role.value,
        telephone=new_user.telephone,
        garage_id=new_user.garage_id,
        token=access_token
    )


@router.post("/login", response_model=UserResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    try:
        user = get_user_by_email(db, login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier le mot de passe
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur de configuration du compte utilisateur"
            )
        
        # Vérifier si le hash est un hash bcrypt valide
        try:
            password_valid = verify_password(login_data.password, user.password_hash)
        except Exception as e:
            error_str = str(e)
            print(f"Erreur lors de la vérification du mot de passe: {error_str}")
            # Si le hash n'est pas un hash bcrypt valide, essayer de re-hasher le mot de passe
            if "password cannot be longer than 72 bytes" in error_str or "Invalid hash" in error_str:
                # Le hash existant n'est probablement pas un hash bcrypt valide
                # On peut essayer de comparer directement si c'était un mot de passe en clair
                # Mais pour la sécurité, on refuse la connexion
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erreur de configuration du compte. Veuillez réinitialiser votre mot de passe."
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier que le rôle existe
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rôle utilisateur non défini"
            )
        
        # Créer un token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return UserResponse(
            id=user.id,
            nom_complet=user.nom_complet,
            email=user.email,
            role=user.role.value,
            telephone=user.telephone,
            garage_id=user.garage_id,
            token=access_token
        )
    except HTTPException:
        # Re-lancer les HTTPException telles quelles
        raise
    except Exception as e:
        # Capturer toutes les autres erreurs et retourner une erreur 500 avec détails
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la connexion: {error_str}")
        print(traceback.format_exc())
        
        # Messages d'erreur plus clairs selon le type d'erreur
        if "Can't connect to MySQL" in error_str or "Connection refused" in error_str:
            detail = "Impossible de se connecter à la base de données. Vérifiez que MySQL/XAMPP est démarré."
        elif "Table" in error_str and "doesn't exist" in error_str:
            detail = "La table utilisateurs n'existe pas. Exécutez le script create_users_table.sql ou py check_database.py"
        else:
            detail = f"Erreur serveur: {error_str[:100]}"  # Limiter la longueur du message
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupère l'utilisateur actuellement connecté"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants"
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(Utilisateur).filter(Utilisateur.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=user.id,
        nom_complet=user.nom_complet,
        email=user.email,
        role=user.role.value,
        telephone=user.telephone,
        garage_id=user.garage_id
    )
