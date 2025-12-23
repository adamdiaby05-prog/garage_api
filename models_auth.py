from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class RoleEnum(str, enum.Enum):
    client = "client"
    garage = "garage"
    admin = "admin"
    gerant = "gerant"
    mecanicien = "mecanicien"
    vendeur = "vendeur"
    secretaire = "secretaire"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    
    # Utiliser __mapper_args__ pour mapper uniquement les colonnes qui existent
    __mapper_args__ = {
        'exclude_properties': ['nom_complet', 'password_hash']  # Colonnes qui n'existent pas
    }
    
    id = Column(Integer, primary_key=True, index=True)
    # Structure réelle de la base de données (comme dans garage-frontend)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    # NE PAS définir nom_complet comme colonne - elle n'existe pas dans la base
    # On la construira uniquement via la propriété full_name
    email = Column(String(150), nullable=False, unique=True, index=True)
    # Utiliser uniquement mot_de_passe (nom réel dans la base)
    mot_de_passe = Column(String(255), nullable=True)  # Nom réel dans la base
    # NE PAS définir password_hash comme colonne - utiliser uniquement mot_de_passe
    # Utiliser String pour le rôle car la base peut avoir d'autres valeurs (gerant, mecanicien, etc.)
    role = Column(String(50), nullable=True, default='client')
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
        """Retourne le mot de passe depuis mot_de_passe"""
        return self.mot_de_passe
    
    @property
    def password_hash(self):
        """Alias pour mot_de_passe (pour compatibilité avec le code existant)"""
        return self.mot_de_passe
    
    # Relations possibles
    # clients = relationship("Client", back_populates="utilisateur")
