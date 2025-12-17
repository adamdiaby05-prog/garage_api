from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Reparation, Client, Vehicule, Employe
from schemas import ReparationCreate, ReparationUpdate, Reparation as ReparationSchema
from sqlalchemy import func

router = APIRouter(prefix="/reparations", tags=["reparations"])


@router.get("/", response_model=List[ReparationSchema])
def get_reparations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des réparations avec pagination et filtres"""
    query = db.query(Reparation)
    
    if client_id:
        query = query.filter(Reparation.client_id == client_id)
    
    if statut:
        query = query.filter(Reparation.statut == statut)
    
    reparations = query.order_by(Reparation.date_debut.desc()).offset(skip).limit(limit).all()
    return reparations


@router.get("/{reparation_id}", response_model=ReparationSchema)
def get_reparation(reparation_id: int, db: Session = Depends(get_db)):
    """Récupère une réparation par son ID"""
    reparation = db.query(Reparation).filter(Reparation.id == reparation_id).first()
    if not reparation:
        raise HTTPException(status_code=404, detail="Réparation non trouvée")
    return reparation


@router.post("/", response_model=ReparationSchema, status_code=201)
def create_reparation(reparation: ReparationCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle réparation"""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == reparation.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier que le véhicule existe
    vehicule = db.query(Vehicule).filter(Vehicule.id == reparation.vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Vérifier que le véhicule appartient au client
    if vehicule.client_id != reparation.client_id:
        raise HTTPException(
            status_code=400,
            detail="Le véhicule n'appartient pas au client spécifié"
        )
    
    # Vérifier l'employé si fourni
    if reparation.employe_id:
        employe = db.query(Employe).filter(Employe.id == reparation.employe_id).first()
        if not employe:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    # Générer le numéro de réparation
    year = datetime.now().year
    count = db.query(func.count(Reparation.id)).filter(
        func.year(Reparation.created_at) == year
    ).scalar()
    numero = f"REP-{year}-{str(count + 1).zfill(4)}"
    
    db_reparation = Reparation(
        **reparation.dict(),
        numero=numero
    )
    db.add(db_reparation)
    db.commit()
    db.refresh(db_reparation)
    return db_reparation


@router.put("/{reparation_id}", response_model=ReparationSchema)
def update_reparation(
    reparation_id: int,
    reparation_update: ReparationUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une réparation"""
    db_reparation = db.query(Reparation).filter(Reparation.id == reparation_id).first()
    if not db_reparation:
        raise HTTPException(status_code=404, detail="Réparation non trouvée")
    
    # Vérifier le client si modifié
    if reparation_update.client_id:
        client = db.query(Client).filter(Client.id == reparation_update.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier le véhicule si modifié
    if reparation_update.vehicule_id:
        vehicule = db.query(Vehicule).filter(Vehicule.id == reparation_update.vehicule_id).first()
        if not vehicule:
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Vérifier l'employé si modifié
    if reparation_update.employe_id:
        employe = db.query(Employe).filter(Employe.id == reparation_update.employe_id).first()
        if not employe:
            raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    update_data = reparation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reparation, field, value)
    
    db.commit()
    db.refresh(db_reparation)
    return db_reparation


@router.delete("/{reparation_id}", status_code=204)
def delete_reparation(reparation_id: int, db: Session = Depends(get_db)):
    """Supprime une réparation"""
    db_reparation = db.query(Reparation).filter(Reparation.id == reparation_id).first()
    if not db_reparation:
        raise HTTPException(status_code=404, detail="Réparation non trouvée")
    
    db.delete(db_reparation)
    db.commit()
    return None

