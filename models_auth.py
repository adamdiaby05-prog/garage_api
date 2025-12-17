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
    nom_complet = Column(String(200), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.client)
    telephone = Column(String(20), nullable=True)
    garage_id = Column(Integer, nullable=True)  # ID du garage si l'utilisateur est un garage
    created_at = Column(String(50), server_default=func.now())
    
    # Relations possibles
    # clients = relationship("Client", back_populates="utilisateur")
