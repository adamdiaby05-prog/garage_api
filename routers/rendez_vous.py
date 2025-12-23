from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Union
from datetime import datetime, date
from database import get_db
from models import RendezVous, Client, Vehicule, Employe, Service, DemandePrestation
from schemas import RendezVousCreate, RendezVousUpdate, RendezVous as RendezVousSchema

router = APIRouter(prefix="/rendez-vous", tags=["rendez-vous"])


@router.get("/")
def get_rendez_vous(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    employe_id: Optional[int] = Query(None),
    garage_id: Optional[int] = Query(None),
    date_rdv: Optional[date] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des rendez-vous ou demandes de prestations avec pagination et filtres"""
    # Si garage_id est fourni, retourner les demandes de prestations au lieu des rendez-vous
    if garage_id:
        query = db.query(DemandePrestation).filter(DemandePrestation.garage_id == garage_id)
        
        if client_id:
            query = query.filter(DemandePrestation.client_id == client_id)
        
        if statut:
            query = query.filter(DemandePrestation.statut == statut)
        
        if date_rdv:
            query = query.filter(
                func.date(DemandePrestation.date_souhaitee) == date_rdv
            )
        
        demandes = query.order_by(DemandePrestation.date_demande.desc()).offset(skip).limit(limit).all()
        
        # Convertir les demandes en format compatible avec RendezVous pour le mobile
        result = []
        for demande in demandes:
            result.append({
                "id": demande.id,
                "client_id": demande.client_id,
                "vehicule_id": demande.vehicule_id,
                "service_id": demande.service_id,
                "employe_id": None,
                "date_rdv": demande.date_souhaitee or demande.date_demande,
                "motif": demande.description_probleme,
                "statut": demande.statut,
                "notes": demande.description_probleme,
                "duree_estimee": demande.duree_estimee or 60,
                "created_at": demande.created_at
            })
        return result
    
    # Sinon, retourner les rendez-vous normaux
    query = db.query(RendezVous)
    
    if client_id:
        query = query.filter(RendezVous.client_id == client_id)
    
    if employe_id:
        query = query.filter(RendezVous.employe_id == employe_id)
    
    if date_rdv:
        query = query.filter(
            func.date(RendezVous.date_rdv) == date_rdv
        )
    
    if statut:
        query = query.filter(RendezVous.statut == statut)
    
    rendez_vous = query.order_by(RendezVous.date_rdv.asc()).offset(skip).limit(limit).all()
    return rendez_vous


@router.get("/{rendez_vous_id}", response_model=RendezVousSchema)
def get_rendez_vous_by_id(rendez_vous_id: int, db: Session = Depends(get_db)):
    """Récupère un rendez-vous par son ID"""
    rendez_vous = db.query(RendezVous).filter(RendezVous.id == rendez_vous_id).first()
    if not rendez_vous:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    return rendez_vous


@router.get("/aujourdhui/liste", response_model=List[RendezVousSchema])
def get_rendez_vous_aujourdhui(db: Session = Depends(get_db)):
    """Récupère les rendez-vous du jour"""
    aujourdhui = date.today()
    rendez_vous = db.query(RendezVous).filter(
        func.date(RendezVous.date_rdv) == aujourdhui
    ).order_by(RendezVous.date_rdv.asc()).all()
    return rendez_vous


@router.post("/", response_model=RendezVousSchema, status_code=201)
def create_rendez_vous(rendez_vous: RendezVousCreate, db: Session = Depends(get_db)):
    """Crée un nouveau rendez-vous"""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == rendez_vous.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier que le véhicule existe
    vehicule = db.query(Vehicule).filter(Vehicule.id == rendez_vous.vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Vérifier que le véhicule appartient au client
    if vehicule.client_id != rendez_vous.client_id:
        raise HTTPException(
            status_code=400,
            detail="Le véhicule n'appartient pas au client spécifié"
        )
    
    # Vérifier l'employé si fourni
    if rendez_vous.employe_id:
        employe = db.query(Employe).filter(Employe.id == rendez_vous.employe_id).first()
        if not employe:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier le service si fourni
    if rendez_vous.service_id:
        service = db.query(Service).filter(Service.id == rendez_vous.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Retirer garage_id du dict car il n'existe pas dans la table
    rendez_vous_data = rendez_vous.dict(exclude={'garage_id'})
    db_rendez_vous = RendezVous(**rendez_vous_data)
    db.add(db_rendez_vous)
    db.commit()
    db.refresh(db_rendez_vous)
    return db_rendez_vous


@router.put("/{rendez_vous_id}", response_model=RendezVousSchema)
def update_rendez_vous(
    rendez_vous_id: int,
    rendez_vous_update: RendezVousUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un rendez-vous"""
    db_rendez_vous = db.query(RendezVous).filter(RendezVous.id == rendez_vous_id).first()
    if not db_rendez_vous:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    
    # Vérifier le client si modifié
    if rendez_vous_update.client_id:
        client = db.query(Client).filter(Client.id == rendez_vous_update.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier le véhicule si modifié
    if rendez_vous_update.vehicule_id:
        vehicule = db.query(Vehicule).filter(Vehicule.id == rendez_vous_update.vehicule_id).first()
        if not vehicule:
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Vérifier l'employé si modifié
    if rendez_vous_update.employe_id:
        employe = db.query(Employe).filter(Employe.id == rendez_vous_update.employe_id).first()
        if not employe:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Vérifier le service si modifié
    if rendez_vous_update.service_id:
        service = db.query(Service).filter(Service.id == rendez_vous_update.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service non trouvé")
    
    update_data = rendez_vous_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rendez_vous, field, value)
    
    db.commit()
    db.refresh(db_rendez_vous)
    return db_rendez_vous


@router.delete("/{rendez_vous_id}", status_code=204)
def delete_rendez_vous(rendez_vous_id: int, db: Session = Depends(get_db)):
    """Supprime un rendez-vous"""
    db_rendez_vous = db.query(RendezVous).filter(RendezVous.id == rendez_vous_id).first()
    if not db_rendez_vous:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    
    db.delete(db_rendez_vous)
    db.commit()
    return None

