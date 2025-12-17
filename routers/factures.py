from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from database import get_db
from models import Facture, Client, Reparation
from schemas import FactureCreate, FactureUpdate, Facture as FactureSchema
from sqlalchemy import func

router = APIRouter(prefix="/factures", tags=["factures"])


@router.get("/", response_model=List[FactureSchema])
def get_factures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des factures avec pagination et filtres"""
    query = db.query(Facture)
    
    if client_id:
        query = query.filter(Facture.client_id == client_id)
    
    if statut:
        query = query.filter(Facture.statut == statut)
    
    factures = query.order_by(Facture.date_facture.desc()).offset(skip).limit(limit).all()
    return factures


@router.get("/{facture_id}", response_model=FactureSchema)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    """Récupère une facture par son ID"""
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.post("/", response_model=FactureSchema, status_code=201)
def create_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle facture"""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == facture.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier la réparation si fournie
    if facture.reparation_id:
        reparation = db.query(Reparation).filter(Reparation.id == facture.reparation_id).first()
        if not reparation:
            raise HTTPException(status_code=404, detail="Réparation non trouvée")
    
    # Générer le numéro de facture
    year = datetime.now().year
    count = db.query(func.count(Facture.id)).filter(
        func.year(Facture.created_at) == year
    ).scalar()
    numero = f"FAC-{year}-{str(count + 1).zfill(4)}"
    
    db_facture = Facture(
        **facture.dict(),
        numero=numero
    )
    db.add(db_facture)
    db.commit()
    db.refresh(db_facture)
    return db_facture


@router.put("/{facture_id}", response_model=FactureSchema)
def update_facture(
    facture_id: int,
    facture_update: FactureUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une facture"""
    db_facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not db_facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    # Vérifier le client si modifié
    if facture_update.client_id:
        client = db.query(Client).filter(Client.id == facture_update.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier la réparation si modifiée
    if facture_update.reparation_id:
        reparation = db.query(Reparation).filter(Reparation.id == facture_update.reparation_id).first()
        if not reparation:
            raise HTTPException(status_code=404, detail="Réparation non trouvée")
    
    update_data = facture_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_facture, field, value)
    
    db.commit()
    db.refresh(db_facture)
    return db_facture


@router.delete("/{facture_id}", status_code=204)
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    """Supprime une facture"""
    db_facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not db_facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    db.delete(db_facture)
    db.commit()
    return None

