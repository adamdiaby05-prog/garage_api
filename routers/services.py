from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Service
from schemas import ServiceCreate, ServiceUpdate, Service as ServiceSchema
from sqlalchemy import or_

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=List[ServiceSchema])
def get_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    categorie: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des services avec pagination et filtres"""
    query = db.query(Service)
    
    if categorie:
        query = query.filter(Service.categorie == categorie)
    
    if statut:
        query = query.filter(Service.statut == statut)
    
    if search:
        query = query.filter(
            or_(
                Service.nom.ilike(f"%{search}%"),
                Service.description.ilike(f"%{search}%")
            )
        )
    
    services = query.offset(skip).limit(limit).all()
    return services


@router.get("/{service_id}", response_model=ServiceSchema)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Récupère un service par son ID"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    return service


@router.post("/", response_model=ServiceSchema, status_code=201)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Crée un nouveau service"""
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.put("/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    update_data = service_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Supprime un service"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    db.delete(db_service)
    db.commit()
    return None

