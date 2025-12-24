from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Schémas de base
class ClientBase(BaseModel):
    nom: str = Field(..., max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    telephone: str = Field(..., max_length=20)
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)


class Client(ClientBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Employe
class EmployeBase(BaseModel):
    nom: str = Field(..., max_length=100)
    prenom: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = "mecanicien"
    salaire: Optional[Decimal] = None
    date_embauche: Optional[date] = None
    statut: Optional[str] = "actif"


class EmployeCreate(EmployeBase):
    pass


class EmployeUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    salaire: Optional[Decimal] = None
    date_embauche: Optional[date] = None
    statut: Optional[str] = None


class Employe(EmployeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Vehicule
class VehiculeBase(BaseModel):
    client_id: int
    marque: str = Field(..., max_length=50)
    modele: str = Field(..., max_length=50)
    immatriculation: str = Field(..., max_length=15)
    annee: Optional[int] = None
    kilometrage: Optional[int] = 0
    carburant: Optional[str] = "essence"
    couleur: Optional[str] = Field(None, max_length=30)
    # photo_url retiré car la colonne n'existe pas dans la base de données
    # photo_url: Optional[str] = None


class VehiculeCreate(VehiculeBase):
    pass


class VehiculeUpdate(BaseModel):
    client_id: Optional[int] = None
    marque: Optional[str] = Field(None, max_length=50)
    modele: Optional[str] = Field(None, max_length=50)
    immatriculation: Optional[str] = Field(None, max_length=15)
    annee: Optional[int] = None
    kilometrage: Optional[int] = None
    carburant: Optional[str] = None
    couleur: Optional[str] = Field(None, max_length=30)
    photo_url: Optional[str] = None


class Vehicule(VehiculeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Service
class ServiceBase(BaseModel):
    nom: str = Field(..., max_length=100)
    description: Optional[str] = None
    categorie: Optional[str] = "maintenance"
    prix: Decimal
    duree_minutes: Optional[int] = 60
    statut: Optional[str] = "actif"


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    categorie: Optional[str] = None
    prix: Optional[Decimal] = None
    duree_minutes: Optional[int] = None
    statut: Optional[str] = None


class Service(ServiceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Piece
class PieceBase(BaseModel):
    reference: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=200)
    categorie: Optional[str] = "accessoires"
    fournisseur: Optional[str] = Field(None, max_length=100)
    prix_achat: Optional[Decimal] = None
    prix_vente: Decimal
    stock_actuel: Optional[int] = 0
    stock_minimum: Optional[int] = 5
    image_url: Optional[str] = None


class PieceCreate(PieceBase):
    pass


class PieceUpdate(BaseModel):
    reference: Optional[str] = Field(None, max_length=50)
    nom: Optional[str] = Field(None, max_length=200)
    categorie: Optional[str] = None
    fournisseur: Optional[str] = Field(None, max_length=100)
    prix_achat: Optional[Decimal] = None
    prix_vente: Optional[Decimal] = None
    stock_actuel: Optional[int] = None
    stock_minimum: Optional[int] = None
    image_url: Optional[str] = None


class Piece(PieceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Reparation
class ReparationBase(BaseModel):
    client_id: int
    vehicule_id: int
    employe_id: Optional[int] = None
    probleme: Optional[str] = None
    diagnostic: Optional[str] = None
    statut: Optional[str] = "ouvert"
    notes: Optional[str] = None


class ReparationCreate(ReparationBase):
    pass


class ReparationUpdate(BaseModel):
    client_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    employe_id: Optional[int] = None
    date_fin: Optional[datetime] = None
    probleme: Optional[str] = None
    diagnostic: Optional[str] = None
    statut: Optional[str] = None
    total_ht: Optional[Decimal] = None
    total_ttc: Optional[Decimal] = None
    notes: Optional[str] = None


class Reparation(ReparationBase):
    id: int
    numero: str
    date_debut: datetime
    date_fin: Optional[datetime] = None
    total_ht: Decimal
    total_ttc: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour PieceUtilisee
class PieceUtiliseeBase(BaseModel):
    reparation_id: int
    piece_id: int
    quantite: Optional[int] = 1
    prix_unitaire: Decimal


class PieceUtiliseeCreate(PieceUtiliseeBase):
    pass


class PieceUtilisee(PieceUtiliseeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Facture
class FactureBase(BaseModel):
    client_id: int
    reparation_id: Optional[int] = None
    date_facture: date
    total_ht: Decimal
    total_ttc: Decimal
    statut: Optional[str] = "brouillon"
    mode_paiement: Optional[str] = None
    notes: Optional[str] = None


class FactureCreate(FactureBase):
    pass


class FactureUpdate(BaseModel):
    client_id: Optional[int] = None
    reparation_id: Optional[int] = None
    date_facture: Optional[date] = None
    total_ht: Optional[Decimal] = None
    total_ttc: Optional[Decimal] = None
    statut: Optional[str] = None
    mode_paiement: Optional[str] = None
    notes: Optional[str] = None


class Facture(FactureBase):
    id: int
    numero: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour RendezVous
class RendezVousBase(BaseModel):
    client_id: int
    vehicule_id: int
    employe_id: Optional[int] = None
    service_id: Optional[int] = None
    # garage_id n'existe pas dans la table rendez_vous - retiré
    date_rdv: datetime
    motif: Optional[str] = None
    statut: Optional[str] = "programme"
    notes: Optional[str] = None
    duree_estimee: Optional[int] = 60


class RendezVousCreate(RendezVousBase):
    pass


class RendezVousUpdate(BaseModel):
    client_id: Optional[int] = None
    vehicule_id: Optional[int] = None
    employe_id: Optional[int] = None
    service_id: Optional[int] = None
    date_rdv: Optional[datetime] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    duree_estimee: Optional[int] = None


class RendezVous(RendezVousBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schémas pour Garage
class GarageBase(BaseModel):
    nom_garage: str = Field(..., max_length=200)
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    siret: Optional[str] = Field(None, max_length=14)
    specialites: Optional[str] = None
    statut: Optional[str] = "en_attente"


class GarageCreate(GarageBase):
    pass


class GarageUpdate(BaseModel):
    nom_garage: Optional[str] = Field(None, max_length=200)
    adresse: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    siret: Optional[str] = Field(None, max_length=14)
    specialites: Optional[str] = None
    statut: Optional[str] = None


class Garage(GarageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

