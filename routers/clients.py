from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, Client as ClientSchema
from sqlalchemy import or_

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=List[ClientSchema])
def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des clients avec pagination et recherche"""
    try:
        query = db.query(Client)
        
        if search:
            query = query.filter(
                or_(
                    Client.nom.ilike(f"%{search}%"),
                    Client.prenom.ilike(f"%{search}%"),
                    Client.email.ilike(f"%{search}%"),
                    Client.telephone.ilike(f"%{search}%")
                )
            )
        
        clients = query.offset(skip).limit(limit).all()
        return clients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/{client_id}", response_model=ClientSchema)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Récupère un client par son ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.post("/", response_model=ClientSchema, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Crée un nouveau client"""
    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.put("/{client_id}", response_model=ClientSchema)
def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Supprime un client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    db.delete(db_client)
    db.commit()
    return None

