from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Garage
from schemas import Garage as GarageSchema, GarageUpdate

router = APIRouter(prefix="/garages", tags=["garages"])


@router.get("/", response_model=List[GarageSchema])
def get_garages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupère la liste des garages"""
    garages = db.query(Garage).offset(skip).limit(limit).all()
    return garages


@router.get("/{garage_id}", response_model=GarageSchema)
def get_garage(garage_id: int, db: Session = Depends(get_db)):
    """Récupère un garage par son ID"""
    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage non trouvé")
    return garage


@router.put("/{garage_id}", response_model=GarageSchema)
def update_garage(
    garage_id: int,
    garage_update: GarageUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un garage"""
    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = garage_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(garage, field, value)
    
    db.commit()
    db.refresh(garage)
    return garage

