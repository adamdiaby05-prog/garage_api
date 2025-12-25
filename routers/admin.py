from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models_auth import Utilisateur
from models import Service, Piece

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete("/users/all")
def delete_all_users(db: Session = Depends(get_db)):
    """Supprime tous les utilisateurs (sauf les admins)"""
    try:
        # Supprimer tous les utilisateurs sauf ceux avec le rôle admin
        result = db.execute(
            text("DELETE FROM utilisateurs WHERE role != 'admin'")
        )
        db.commit()
        deleted_count = result.rowcount
        return {
            "success": True,
            "message": f"{deleted_count} utilisateur(s) supprimé(s)",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la suppression des utilisateurs: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression des utilisateurs: {error_str}"
        )


@router.delete("/services/all")
def delete_all_services(db: Session = Depends(get_db)):
    """Supprime tous les services"""
    try:
        result = db.execute(text("DELETE FROM services"))
        db.commit()
        deleted_count = result.rowcount
        return {
            "success": True,
            "message": f"{deleted_count} service(s) supprimé(s)",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la suppression des services: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression des services: {error_str}"
        )


@router.delete("/pieces/all")
def delete_all_pieces(db: Session = Depends(get_db)):
    """Supprime toutes les pièces (produits de la boutique)"""
    try:
        result = db.execute(text("DELETE FROM pieces"))
        db.commit()
        deleted_count = result.rowcount
        return {
            "success": True,
            "message": f"{deleted_count} pièce(s) supprimée(s)",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la suppression des pièces: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression des pièces: {error_str}"
        )

