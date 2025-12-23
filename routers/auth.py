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
from models import Client
from sqlalchemy import or_

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
def get_user_full_name(user) -> str:
    """Construit le nom complet depuis nom_complet ou nom+prenom"""
    if hasattr(user, 'nom_complet') and user.nom_complet:
        return user.nom_complet
    nom_parts = []
    if hasattr(user, 'prenom') and user.prenom:
        nom_parts.append(user.prenom)
    if hasattr(user, 'nom') and user.nom:
        nom_parts.append(user.nom)
    return ' '.join(nom_parts) if nom_parts else (user.email if hasattr(user, 'email') else '')

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
    """Récupère un utilisateur par email (le plus récent en cas de doublons)"""
    try:
        # Récupérer tous les utilisateurs avec cet email (en cas de doublons)
        users = db.query(Utilisateur).filter(Utilisateur.email == email).order_by(Utilisateur.id.desc()).all()
        
        if not users:
            return None
        
        # Si plusieurs utilisateurs avec le même email, utiliser le plus récent (ID le plus élevé)
        if len(users) > 1:
            print(f"⚠️  ATTENTION: {len(users)} utilisateurs trouvés avec l'email '{email}'. Utilisation du plus récent (ID: {users[0].id})")
            # Optionnel: vous pouvez supprimer les anciens doublons ici
            # for old_user in users[1:]:
            #     db.delete(old_user)
            # db.commit()
        
        return users[0]
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
    
    # Créer l'utilisateur avec la structure réelle de la base (nom/prenom)
    # Créer l'utilisateur avec la structure réelle de la base (nom/prenom, mot_de_passe)
    new_user = Utilisateur(
        email=user_data.email,
        mot_de_passe=hashed_password,  # Utiliser mot_de_passe (nom réel dans la base)
        role=RoleEnum(user_data.role),
        telephone=user_data.telephone,
        nom=nom,
        prenom=prenom
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Si l'utilisateur est un client, créer automatiquement un enregistrement dans la table clients
    client_id = None
    if new_user.role == RoleEnum.client:
        # Vérifier si un client avec cet email existe déjà
        existing_client = db.query(Client).filter(Client.email == new_user.email).first()
        if existing_client:
            client_id = existing_client.id
        else:
            # Créer un nouveau client
            # Utiliser nom/prenom du new_user ou construire depuis nom_complet
            client_nom = new_user.nom or (nom_parts[0] if nom_parts else '')
            client_prenom = new_user.prenom or (nom_parts[1] if len(nom_parts) > 1 else None)
            
            new_client = Client(
                nom=client_nom,
                prenom=client_prenom,
                email=new_user.email,
                telephone=new_user.telephone or "0000000000"  # Téléphone obligatoire dans Client
            )
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            client_id = new_client.id
    
    # Créer un token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role.value},
        expires_delta=access_token_expires
    )
    
    return UserResponse(
        id=new_user.id,
        nom_complet=get_user_full_name(new_user),
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
        
        # Vérifier le mot de passe (utiliser mot_de_passe directement)
        password_hash = user.mot_de_passe
        if not password_hash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur de configuration du compte utilisateur"
            )
        
        # Vérifier si le hash est un hash bcrypt valide
        try:
            password_valid = verify_password(login_data.password, password_hash)
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
        
        # IMPORTANT: Vérifier d'abord si un garage existe avec cet email
        # Si oui, l'utilisateur DOIT être un garage, peu importe son rôle dans la base
        from models import Garage
        garage = db.query(Garage).filter(Garage.email == user.email).first()
        
        if garage:
            # Un garage existe avec cet email, l'utilisateur DOIT être un garage
            if user.role != RoleEnum.garage or user.garage_id != garage.id:
                print(f"⚠️  Garage trouvé pour {user.email} (ID: {garage.id})")
                print(f"   Correction: rôle={user.role.value} → 'garage', garage_id={user.garage_id} → {garage.id}")
                user.role = RoleEnum.garage
                user.garage_id = garage.id
                db.commit()
                db.refresh(user)
        else:
            # Pas de garage avec cet email
            # Cohérence rôle/garage_id : si l'utilisateur a un garage_id, son rôle doit être "garage"
            if user.garage_id and user.role != RoleEnum.garage:
                print(f"⚠️  Incohérence détectée: utilisateur {user.email} a garage_id={user.garage_id} mais rôle={user.role.value}")
                print(f"   Correction automatique: rôle changé en 'garage'")
                user.role = RoleEnum.garage
                db.commit()
                db.refresh(user)
            
            # Si l'utilisateur est un garage mais n'a pas de garage_id, c'est une incohérence
            if user.role == RoleEnum.garage and not user.garage_id:
                print(f"⚠️  ATTENTION: Utilisateur {user.email} a le rôle 'garage' mais pas de garage_id et aucun garage trouvé avec cet email")
                print(f"   Le rôle sera retourné tel quel, mais l'utilisateur n'a pas de garage associé")
        
        # Créer un token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return UserResponse(
            id=user.id,
            nom_complet=get_user_full_name(user),
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


@router.get("/client-id")
def get_client_id_from_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupère ou crée le client_id associé à l'utilisateur connecté"""
    try:
        # Décoder le token pour obtenir l'ID de l'utilisateur
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user_email = payload.get("email")
        user_role = payload.get("role")
        
        # Vérifier que l'utilisateur est un client
        if user_role != "client":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cette fonctionnalité est réservée aux clients"
            )
        
        # Récupérer l'utilisateur
        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Chercher le client par email
        client = db.query(Client).filter(Client.email == user.email).first()
        
        if not client:
            # Créer le client s'il n'existe pas
            # Utiliser directement nom et prenom depuis l'utilisateur
            nom = user.nom or ''
            prenom = user.prenom or None
            
            new_client = Client(
                nom=nom,
                prenom=prenom,
                email=user.email,
                telephone=user.telephone or "0000000000"
            )
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            return {"client_id": new_client.id}
        
        return {"client_id": client.id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.put("/update-garage-id", response_model=UserResponse)
def update_user_garage_id(
    garage_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Met à jour le garage_id de l'utilisateur connecté"""
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
    
    # Vérifier que le garage existe
    from models import Garage
    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if garage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garage non trouvé"
        )
    
    # Mettre à jour le garage_id de l'utilisateur
    user.garage_id = garage_id
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        nom_complet=get_user_full_name(user),
        email=user.email,
        role=user.role.value,
        telephone=user.telephone,
        garage_id=user.garage_id
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
    
    # Appliquer la même logique de cohérence que dans login
    from models import Garage
    garage = db.query(Garage).filter(Garage.email == user.email).first()
    
    if garage:
        # Un garage existe avec cet email, l'utilisateur DOIT être un garage
        if user.role != RoleEnum.garage or user.garage_id != garage.id:
            user.role = RoleEnum.garage
            user.garage_id = garage.id
            db.commit()
            db.refresh(user)
    else:
        # Cohérence rôle/garage_id
        if user.garage_id and user.role != RoleEnum.garage:
            user.role = RoleEnum.garage
            db.commit()
            db.refresh(user)
    
    return UserResponse(
        id=user.id,
        nom_complet=user.nom_complet,
        email=user.email,
        role=user.role.value,
        telephone=user.telephone,
        garage_id=user.garage_id
    )
