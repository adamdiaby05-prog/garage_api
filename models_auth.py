from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class RoleEnum(str, enum.Enum):
    client = "client"
    garage = "garage"
    admin = "admin"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    
    id = Column(Integer, primary_key=True, index=True)
    # Structure réelle de la base de données (comme dans garage-frontend)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    # NE PAS définir nom_complet comme colonne - elle n'existe pas dans la base
    # On la construira uniquement via la propriété full_name
    email = Column(String(150), nullable=False, unique=True, index=True)
    # Support des deux noms de colonnes pour le mot de passe
    mot_de_passe = Column(String(255), nullable=True)  # Nom réel dans la base
    password_hash = Column(String(255), nullable=True)  # Alias pour compatibilité
    role = Column(Enum(RoleEnum), default=RoleEnum.client)
    telephone = Column(String(30), nullable=True)
    garage_id = Column(Integer, nullable=True)
    created_at = Column(String(50), server_default=func.now())
    
    @property
    def nom_complet(self):
        """Construit le nom complet depuis nom+prenom (propriété calculée, pas une colonne)"""
        nom_parts = []
        if self.prenom:
            nom_parts.append(self.prenom)
        if self.nom:
            nom_parts.append(self.nom)
        return ' '.join(nom_parts) if nom_parts else (self.email or '')
    
    @property
    def full_name(self):
        """Alias pour nom_complet"""
        return self.nom_complet
    
    @property
    def password(self):
        """Retourne le mot de passe depuis password_hash ou mot_de_passe"""
        return self.password_hash or self.mot_de_passe
    
    # Relations possibles
    # clients = relationship("Client", back_populates="utilisateur")
