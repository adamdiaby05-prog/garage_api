from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Piece
from schemas import PieceCreate, PieceUpdate, Piece as PieceSchema
from sqlalchemy import or_

router = APIRouter(prefix="/pieces", tags=["pieces"])


@router.get("/", response_model=List[PieceSchema])
def get_pieces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    categorie: Optional[str] = Query(None),
    stock_critique: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la liste des pièces avec pagination et filtres"""
    query = db.query(Piece)
    
    if categorie:
        query = query.filter(Piece.categorie == categorie)
    
    if stock_critique:
        query = query.filter(Piece.stock_actuel <= Piece.stock_minimum)
    
    if search:
        query = query.filter(
            or_(
                Piece.nom.ilike(f"%{search}%"),
                Piece.reference.ilike(f"%{search}%"),
                Piece.fournisseur.ilike(f"%{search}%")
            )
        )
    
    pieces = query.offset(skip).limit(limit).all()
    return pieces


@router.get("/{piece_id}", response_model=PieceSchema)
def get_piece(piece_id: int, db: Session = Depends(get_db)):
    """Récupère une pièce par son ID"""
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    return piece


@router.post("/", response_model=PieceSchema, status_code=201)
def create_piece(piece: PieceCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle pièce"""
    # Vérifier que la référence n'existe pas déjà
    existing = db.query(Piece).filter(Piece.reference == piece.reference).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Une pièce avec cette référence existe déjà"
        )
    
    db_piece = Piece(**piece.dict())
    db.add(db_piece)
    db.commit()
    db.refresh(db_piece)
    return db_piece


@router.put("/{piece_id}", response_model=PieceSchema)
def update_piece(
    piece_id: int,
    piece_update: PieceUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une pièce"""
    db_piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not db_piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    # Vérifier la référence si modifiée
    if piece_update.reference:
        existing = db.query(Piece).filter(
            Piece.reference == piece_update.reference,
            Piece.id != piece_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Une pièce avec cette référence existe déjà"
            )
    
    update_data = piece_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_piece, field, value)
    
    db.commit()
    db.refresh(db_piece)
    return db_piece


@router.delete("/{piece_id}", status_code=204)
def delete_piece(piece_id: int, db: Session = Depends(get_db)):
    """Supprime une pièce"""
    db_piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not db_piece:
        raise HTTPException(status_code=404, detail="Pièce non trouvée")
    
    db.delete(db_piece)
    db.commit()
    return None


@router.get("/stock/critique", response_model=List[PieceSchema])
def get_stock_critique(db: Session = Depends(get_db)):
    """Récupère les pièces en stock critique"""
    pieces = db.query(Piece).filter(
        Piece.stock_actuel <= Piece.stock_minimum
    ).all()
    return pieces

