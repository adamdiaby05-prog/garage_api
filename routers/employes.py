from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Employe
from schemas import EmployeCreate, EmployeUpdate, Employe as EmployeSchema
from sqlalchemy import or_

router = APIRouter(prefix="/employes", tags=["employes"])


@router.get("/", response_model=List[EmployeSchema])
def get_employes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des employés avec pagination et filtres"""
    query = db.query(Employe)
    
    if role:
        query = query.filter(Employe.role == role)
    
    if statut:
        query = query.filter(Employe.statut == statut)
    
    if search:
        query = query.filter(
            or_(
                Employe.nom.ilike(f"%{search}%"),
                Employe.prenom.ilike(f"%{search}%"),
                Employe.email.ilike(f"%{search}%")
            )
        )
    
    employes = query.offset(skip).limit(limit).all()
    return employes


@router.get("/{employe_id}", response_model=EmployeSchema)
def get_employe(employe_id: int, db: Session = Depends(get_db)):
    """Récupère un employé par son ID"""
    employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    return employe


@router.post("/", response_model=EmployeSchema, status_code=201)
def create_employe(employe: EmployeCreate, db: Session = Depends(get_db)):
    """Crée un nouvel employé"""
    db_employe = Employe(**employe.dict())
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    return db_employe


@router.put("/{employe_id}", response_model=EmployeSchema)
def update_employe(
    employe_id: int,
    employe_update: EmployeUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un employé"""
    db_employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not db_employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    update_data = employe_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employe, field, value)
    
    db.commit()
    db.refresh(db_employe)
    return db_employe


@router.delete("/{employe_id}", status_code=204)
def delete_employe(employe_id: int, db: Session = Depends(get_db)):
    """Supprime un employé"""
    db_employe = db.query(Employe).filter(Employe.id == employe_id).first()
    if not db_employe:
        raise HTTPException(status_code=404, detail="Employé non trouvé")
    
    db.delete(db_employe)
    db.commit()
    return None

