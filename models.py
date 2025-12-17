from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Enum, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base


# Enums
class RoleEnum(str, enum.Enum):
    gerant = "gerant"
    mecanicien = "mecanicien"
    vendeur = "vendeur"
    secretaire = "secretaire"


class StatutEmployeEnum(str, enum.Enum):
    actif = "actif"
    inactif = "inactif"


class CarburantEnum(str, enum.Enum):
    essence = "essence"
    diesel = "diesel"
    hybride = "hybride"
    electrique = "electrique"


class StatutReparationEnum(str, enum.Enum):
    ouvert = "ouvert"
    en_cours = "en_cours"
    termine = "termine"
    facture = "facture"


class StatutFactureEnum(str, enum.Enum):
    brouillon = "brouillon"
    envoyee = "envoyee"
    payee = "payee"


class ModePaiementEnum(str, enum.Enum):
    especes = "especes"
    carte = "carte"
    cheque = "cheque"
    virement = "virement"


class StatutRendezVousEnum(str, enum.Enum):
    programme = "programme"
    en_cours = "en_cours"
    termine = "termine"
    annule = "annule"


class StatutGarageEnum(str, enum.Enum):
    actif = "actif"
    inactif = "inactif"
    en_attente = "en_attente"


# Modèles
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True)
    telephone = Column(String(20), nullable=False)
    adresse = Column(Text, nullable=True)
    ville = Column(String(100), nullable=True)
    code_postal = Column(String(10), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    vehicules = relationship("Vehicule", back_populates="client", cascade="all, delete-orphan")
    reparations = relationship("Reparation", back_populates="client", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="client", cascade="all, delete-orphan")
    rendez_vous = relationship("RendezVous", back_populates="client", cascade="all, delete-orphan")


class Employe(Base):
    __tablename__ = "employes"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), nullable=True)
    telephone = Column(String(20), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.mecanicien)
    salaire = Column(DECIMAL(10, 2), nullable=True)
    date_embauche = Column(Date, nullable=True)
    statut = Column(Enum(StatutEmployeEnum), default=StatutEmployeEnum.actif)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    reparations = relationship("Reparation", back_populates="employe")
    rendez_vous = relationship("RendezVous", back_populates="employe")


class Vehicule(Base):
    __tablename__ = "vehicules"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    marque = Column(String(50), nullable=False)
    modele = Column(String(50), nullable=False)
    immatriculation = Column(String(15), nullable=False, unique=True)
    annee = Column(Integer, nullable=True)
    kilometrage = Column(Integer, default=0)
    carburant = Column(Enum(CarburantEnum), default=CarburantEnum.essence)
    couleur = Column(String(30), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    client = relationship("Client", back_populates="vehicules")
    reparations = relationship("Reparation", back_populates="vehicule", cascade="all, delete-orphan")
    rendez_vous = relationship("RendezVous", back_populates="vehicule", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    categorie = Column(String(50), default="maintenance")
    prix = Column(DECIMAL(10, 2), nullable=False)
    duree_minutes = Column(Integer, default=60)
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    rendez_vous = relationship("RendezVous", back_populates="service")


class Piece(Base):
    __tablename__ = "pieces"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), nullable=False, unique=True)
    nom = Column(String(200), nullable=False)
    categorie = Column(String(50), default="accessoires")
    fournisseur = Column(String(100), nullable=True)
    prix_achat = Column(DECIMAL(10, 2), nullable=True)
    prix_vente = Column(DECIMAL(10, 2), nullable=False)
    stock_actuel = Column(Integer, default=0)
    stock_minimum = Column(Integer, default=5)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    pieces_utilisees = relationship("PieceUtilisee", back_populates="piece")


class Reparation(Base):
    __tablename__ = "reparations"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    vehicule_id = Column(Integer, ForeignKey("vehicules.id"), nullable=False)
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=True)
    date_debut = Column(DateTime, server_default=func.now())
    date_fin = Column(DateTime, nullable=True)
    probleme = Column(Text, nullable=True)
    diagnostic = Column(Text, nullable=True)
    statut = Column(Enum(StatutReparationEnum), default=StatutReparationEnum.ouvert)
    total_ht = Column(DECIMAL(10, 2), default=0.00)
    total_ttc = Column(DECIMAL(10, 2), default=0.00)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    client = relationship("Client", back_populates="reparations")
    vehicule = relationship("Vehicule", back_populates="reparations")
    employe = relationship("Employe", back_populates="reparations")
    pieces_utilisees = relationship("PieceUtilisee", back_populates="reparation", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="reparation")


class PieceUtilisee(Base):
    __tablename__ = "pieces_utilisees"
    
    id = Column(Integer, primary_key=True, index=True)
    reparation_id = Column(Integer, ForeignKey("reparations.id"), nullable=False)
    piece_id = Column(Integer, ForeignKey("pieces.id"), nullable=False)
    quantite = Column(Integer, default=1)
    prix_unitaire = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    reparation = relationship("Reparation", back_populates="pieces_utilisees")
    piece = relationship("Piece", back_populates="pieces_utilisees")


class Facture(Base):
    __tablename__ = "factures"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False, unique=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    reparation_id = Column(Integer, ForeignKey("reparations.id"), nullable=True)
    date_facture = Column(Date, nullable=False)
    total_ht = Column(DECIMAL(10, 2), nullable=False)
    total_ttc = Column(DECIMAL(10, 2), nullable=False)
    statut = Column(Enum(StatutFactureEnum), default=StatutFactureEnum.brouillon)
    mode_paiement = Column(Enum(ModePaiementEnum), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    client = relationship("Client", back_populates="factures")
    reparation = relationship("Reparation", back_populates="factures")


class RendezVous(Base):
    __tablename__ = "rendez_vous"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    vehicule_id = Column(Integer, ForeignKey("vehicules.id"), nullable=False)
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=True)
    date_rdv = Column(DateTime, nullable=False)
    motif = Column(Text, nullable=True)
    statut = Column(Enum(StatutRendezVousEnum), default=StatutRendezVousEnum.programme)
    notes = Column(Text, nullable=True)
    duree_estimee = Column(Integer, default=60)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    client = relationship("Client", back_populates="rendez_vous")
    vehicule = relationship("Vehicule", back_populates="rendez_vous")
    employe = relationship("Employe", back_populates="rendez_vous")
    service = relationship("Service", back_populates="rendez_vous")
    garage = relationship("Garage")


class Garage(Base):
    __tablename__ = "garages"
    
    id = Column(Integer, primary_key=True, index=True)
    nom_garage = Column(String(200), nullable=False)
    adresse = Column(Text, nullable=True)
    ville = Column(String(100), nullable=True)
    code_postal = Column(String(10), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    siret = Column(String(14), nullable=True)
    specialites = Column(Text, nullable=True)
    statut = Column(Enum(StatutGarageEnum), default=StatutGarageEnum.en_attente)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Fournisseur(Base):
    __tablename__ = "fournisseurs"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    adresse = Column(Text, nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    contact = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

