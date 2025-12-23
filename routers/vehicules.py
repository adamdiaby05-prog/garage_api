from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Vehicule, Client
from schemas import VehiculeCreate, VehiculeUpdate, Vehicule as VehiculeSchema
from sqlalchemy import or_

router = APIRouter(prefix="/vehicules", tags=["vehicules"])


@router.get("/", response_model=List[VehiculeSchema])
def get_vehicules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des véhicules avec pagination et filtres"""
    try:
        # Utiliser une requête SQL brute pour charger uniquement les colonnes qui existent
        from sqlalchemy import text
        
        base_query = """
            SELECT id, client_id, marque, modele, immatriculation, annee, kilometrage, carburant, couleur, created_at
            FROM vehicules
        """
        conditions = []
        params = {}
        
        if client_id:
            conditions.append("client_id = :client_id")
            params['client_id'] = client_id
        
        if search:
            conditions.append("(marque LIKE :search OR modele LIKE :search OR immatriculation LIKE :search)")
            params['search'] = f"%{search}%"
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " LIMIT :limit OFFSET :skip"
        params['limit'] = limit
        params['skip'] = skip
        
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        # Construire les objets Vehicule depuis les lignes
        vehicules = []
        for row in rows:
            vehicule = Vehicule(
                id=row[0],
                client_id=row[1],
                marque=row[2],
                modele=row[3],
                immatriculation=row[4],
                annee=row[5] if row[5] else None,
                kilometrage=row[6] if row[6] else 0,
                carburant=str(row[7]) if row[7] else 'essence',
                couleur=row[8] if row[8] else None,
                created_at=row[9] if row[9] else None
            )
            vehicules.append(vehicule)
        
        return vehicules
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la récupération des véhicules: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des véhicules: {error_str}"
        )


@router.get("/{vehicule_id}", response_model=VehiculeSchema)
def get_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    """Récupère un véhicule par son ID"""
    vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return vehicule


@router.post("/", response_model=VehiculeSchema, status_code=201)
def create_vehicule(vehicule: VehiculeCreate, db: Session = Depends(get_db)):
    """Crée un nouveau véhicule"""
    # Vérifier que le client existe
    client = db.query(Client).filter(Client.id == vehicule.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier que l'immatriculation n'existe pas déjà
    existing = db.query(Vehicule).filter(
        Vehicule.immatriculation == vehicule.immatriculation
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Un véhicule avec cette immatriculation existe déjà"
        )
    
    db_vehicule = Vehicule(**vehicule.dict())
    db.add(db_vehicule)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


@router.put("/{vehicule_id}", response_model=VehiculeSchema)
def update_vehicule(
    vehicule_id: int,
    vehicule_update: VehiculeUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour un véhicule"""
    db_vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
    if not db_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    # Vérifier le client si modifié
    if vehicule_update.client_id:
        client = db.query(Client).filter(Client.id == vehicule_update.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier l'immatriculation si modifiée
    if vehicule_update.immatriculation:
        existing = db.query(Vehicule).filter(
            Vehicule.immatriculation == vehicule_update.immatriculation,
            Vehicule.id != vehicule_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Un véhicule avec cette immatriculation existe déjà"
            )
    
    update_data = vehicule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicule, field, value)
    
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


@router.delete("/{vehicule_id}", status_code=204)
def delete_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    """Supprime un véhicule"""
    db_vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
    if not db_vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    
    db.delete(db_vehicule)
    db.commit()
    return None

