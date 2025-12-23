from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import DemandePrestation, Client, Vehicule, Service, Garage


class AcceptDemandeRequest(BaseModel):
    garage_id: int
    prix_estime: Optional[float] = None
    duree_estimee: Optional[int] = None


class UpdateStatutRequest(BaseModel):
    statut: str

router = APIRouter(prefix="/prestations/demandes", tags=["demandes-prestations"])


@router.get("/")
def get_demandes_prestations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    statut: Optional[str] = Query(None),
    garage_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère toutes les demandes de prestations avec les informations des clients, véhicules et services"""
    try:
        # Construire la requête SQL avec les conditions
        base_query = """
            SELECT 
                dp.id,
                dp.client_id,
                dp.vehicule_id,
                dp.service_id,
                dp.garage_id,
                dp.date_demande,
                dp.date_souhaitee,
                dp.description_probleme,
                dp.statut,
                dp.prix_estime,
                dp.duree_estimee,
                dp.created_at,
                dp.updated_at,
                c.nom as client_nom,
                c.prenom as client_prenom,
                c.email as client_email,
                c.telephone as client_telephone,
                v.marque as vehicule_marque,
                v.modele as vehicule_modele,
                v.immatriculation as vehicule_immatriculation,
                s.nom as service_nom,
                s.description as service_description,
                s.prix as service_prix,
                g.nom_garage as garage_nom
            FROM demandes_prestations dp
            LEFT JOIN clients c ON dp.client_id = c.id
            LEFT JOIN vehicules v ON dp.vehicule_id = v.id
            LEFT JOIN services s ON dp.service_id = s.id
            LEFT JOIN garages g ON dp.garage_id = g.id
            WHERE 1=1
        """
        
        params = {}
        conditions = []
        
        if statut:
            conditions.append("dp.statut = :statut")
            params['statut'] = statut
        
        if garage_id:
            conditions.append("dp.garage_id = :garage_id")
            params['garage_id'] = garage_id
        
        if client_id:
            conditions.append("dp.client_id = :client_id")
            params['client_id'] = client_id
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY dp.created_at DESC LIMIT :limit OFFSET :skip"
        params['limit'] = limit
        params['skip'] = skip
        
        print(f"🔍 Requête SQL: {base_query}")
        print(f"🔍 Paramètres: {params}")
        
        result = db.execute(text(base_query), params)
        rows = result.fetchall()
        
        print(f"✅ {len(rows)} demandes de prestations trouvées dans la base de données")
        
        # Construire les dictionnaires avec toutes les informations
        demandes = []
        for row in rows:
            demande_data = {
                "id": row[0],
                "client_id": row[1],
                "vehicule_id": row[2],
                "service_id": row[3],
                "garage_id": row[4] if row[4] else None,
                "date_demande": str(row[5]) if row[5] else None,
                "date_souhaitee": str(row[6]) if row[6] else None,
                "description_probleme": row[7] if row[7] else None,
                "statut": row[8] if row[8] else 'en_attente',
                "prix_estime": float(row[9]) if row[9] else None,
                "duree_estimee": row[10] if row[10] else None,
                "created_at": str(row[11]) if row[11] else None,
                "updated_at": str(row[12]) if row[12] else None,
                # Informations client
                "client_nom": row[13] if row[13] else None,
                "client_prenom": row[14] if row[14] else None,
                "client_email": row[15] if row[15] else None,
                "client_telephone": row[16] if row[16] else None,
                # Informations véhicule
                "marque": row[17] if row[17] else None,
                "modele": row[18] if row[18] else None,
                "immatriculation": row[19] if row[19] else None,
                # Informations service
                "service_nom": row[20] if row[20] else None,
                "service_description": row[21] if row[21] else None,
                "service_prix": float(row[22]) if row[22] else None,
                # Informations garage
                "nom_garage": row[23] if row[23] else None
            }
            demandes.append(demande_data)
        
        return demandes
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la récupération des demandes de prestations: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des demandes de prestations: {error_str}"
        )


@router.get("/{demande_id}")
def get_demande_prestation(demande_id: int, db: Session = Depends(get_db)):
    """Récupère une demande de prestation par son ID"""
    try:
        query = text("""
            SELECT 
                dp.id,
                dp.client_id,
                dp.vehicule_id,
                dp.service_id,
                dp.garage_id,
                dp.date_demande,
                dp.date_souhaitee,
                dp.description_probleme,
                dp.statut,
                dp.prix_estime,
                dp.duree_estimee,
                dp.created_at,
                dp.updated_at,
                c.nom as client_nom,
                c.prenom as client_prenom,
                c.email as client_email,
                c.telephone as client_telephone,
                v.marque as vehicule_marque,
                v.modele as vehicule_modele,
                v.immatriculation as vehicule_immatriculation,
                s.nom as service_nom,
                s.description as service_description,
                s.prix as service_prix,
                g.nom_garage as garage_nom
            FROM demandes_prestations dp
            LEFT JOIN clients c ON dp.client_id = c.id
            LEFT JOIN vehicules v ON dp.vehicule_id = v.id
            LEFT JOIN services s ON dp.service_id = s.id
            LEFT JOIN garages g ON dp.garage_id = g.id
            WHERE dp.id = :demande_id
        """)
        
        result = db.execute(query, {"demande_id": demande_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Demande de prestation non trouvée")
        
        demande_data = {
            "id": row[0],
            "client_id": row[1],
            "vehicule_id": row[2],
            "service_id": row[3],
            "garage_id": row[4] if row[4] else None,
            "date_demande": str(row[5]) if row[5] else None,
            "date_souhaitee": str(row[6]) if row[6] else None,
            "description_probleme": row[7] if row[7] else None,
            "statut": row[8] if row[8] else 'en_attente',
            "prix_estime": float(row[9]) if row[9] else None,
            "duree_estimee": row[10] if row[10] else None,
            "created_at": str(row[11]) if row[11] else None,
            "updated_at": str(row[12]) if row[12] else None,
            "client_nom": row[13] if row[13] else None,
            "client_prenom": row[14] if row[14] else None,
            "client_email": row[15] if row[15] else None,
            "client_telephone": row[16] if row[16] else None,
            "marque": row[17] if row[17] else None,
            "modele": row[18] if row[18] else None,
            "immatriculation": row[19] if row[19] else None,
            "service_nom": row[20] if row[20] else None,
            "service_description": row[21] if row[21] else None,
            "service_prix": float(row[22]) if row[22] else None,
            "nom_garage": row[23] if row[23] else None
        }
        
        return demande_data
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la récupération de la demande de prestation: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la demande de prestation: {error_str}"
        )


@router.patch("/{demande_id}/accept")
def accept_demande_prestation(
    demande_id: int,
    accept_data: AcceptDemandeRequest = Body(...),
    db: Session = Depends(get_db)
):
    """Accepte une demande de prestation et l'assigne à un garage"""
    try:
        # Vérifier que la demande existe
        demande = db.query(DemandePrestation).filter(DemandePrestation.id == demande_id).first()
        if not demande:
            raise HTTPException(status_code=404, detail="Demande de prestation non trouvée")
        
        # Vérifier que le garage existe
        garage = db.query(Garage).filter(Garage.id == accept_data.garage_id).first()
        if not garage:
            raise HTTPException(status_code=404, detail="Garage non trouvé")
        
        # Mettre à jour la demande
        demande.garage_id = accept_data.garage_id
        demande.statut = 'acceptee'
        if accept_data.prix_estime is not None:
            demande.prix_estime = accept_data.prix_estime
        if accept_data.duree_estimee is not None:
            demande.duree_estimee = accept_data.duree_estimee
        
        db.commit()
        db.refresh(demande)
        
        return {
            "success": True,
            "message": "Demande acceptée et assignée au garage avec succès",
            "demande_id": demande.id,
            "garage_id": demande.garage_id,
            "statut": demande.statut
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de l'acceptation de la demande: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'acceptation de la demande: {error_str}"
        )


@router.patch("/{demande_id}/statut")
def update_statut_demande(
    demande_id: int,
    update_data: UpdateStatutRequest = Body(...),
    db: Session = Depends(get_db)
):
    """Met à jour le statut d'une demande de prestation"""
    try:
        demande = db.query(DemandePrestation).filter(DemandePrestation.id == demande_id).first()
        if not demande:
            raise HTTPException(status_code=404, detail="Demande de prestation non trouvée")
        
        # Valider le statut
        statuts_valides = ['en_attente', 'acceptee', 'en_cours', 'terminee', 'annulee']
        if update_data.statut not in statuts_valides:
            raise HTTPException(
                status_code=400,
                detail=f"Statut invalide. Statuts valides: {', '.join(statuts_valides)}"
            )
        
        demande.statut = update_data.statut
        db.commit()
        db.refresh(demande)
        
        return {
            "success": True,
            "message": "Statut mis à jour avec succès",
            "demande_id": demande.id,
            "statut": demande.statut
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la mise à jour du statut: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour du statut: {error_str}"
        )


@router.delete("/{demande_id}")
def delete_demande_prestation(demande_id: int, db: Session = Depends(get_db)):
    """Supprime une demande de prestation"""
    try:
        demande = db.query(DemandePrestation).filter(DemandePrestation.id == demande_id).first()
        if not demande:
            raise HTTPException(status_code=404, detail="Demande de prestation non trouvée")
        
        db.delete(demande)
        db.commit()
        
        return {
            "success": True,
            "message": "Demande supprimée avec succès"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la suppression de la demande: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression de la demande: {error_str}"
        )

