from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import math
from database import get_db
from models import DemandePrestation, Client, Vehicule, Service, Garage, StatutGarageEnum


class AcceptDemandeRequest(BaseModel):
    garage_id: int
    prix_estime: Optional[float] = None
    duree_estimee: Optional[int] = None


class UpdateStatutRequest(BaseModel):
    statut: str


class CreateDemandeRequest(BaseModel):
    client_id: int
    vehicule_id: int
    service_id: int
    date_souhaitee: Optional[datetime] = None
    description_probleme: Optional[str] = None
    client_latitude: float
    client_longitude: float


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en kilomètres entre deux points géographiques (formule de Haversine)"""
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Convertir en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def find_nearest_garage(client_latitude: float, client_longitude: float, db: Session) -> Optional[Garage]:
    """Trouve le garage le plus proche du client"""
    # Récupérer tous les garages avec leur localisation
    garages = db.query(Garage).filter(
        Garage.latitude.isnot(None),
        Garage.longitude.isnot(None),
        Garage.statut == StatutGarageEnum.actif  # Seulement les garages actifs
    ).all()
    
    if not garages:
        return None
    
    # Calculer la distance pour chaque garage et trouver le plus proche
    nearest_garage = None
    min_distance = float('inf')
    
    for garage in garages:
        try:
            garage_lat = float(garage.latitude)
            garage_lon = float(garage.longitude)
            distance = calculate_distance(client_latitude, client_longitude, garage_lat, garage_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest_garage = garage
        except (ValueError, TypeError):
            continue  # Ignorer les garages avec coordonnées invalides
    
    return nearest_garage

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
                dp.client_latitude,
                dp.client_longitude,
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
                g.nom_garage as garage_nom,
                g.latitude as garage_latitude,
                g.longitude as garage_longitude
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
        # Utiliser un set pour éviter les doublons basés sur l'ID
        seen_ids = set()
        demandes = []
        for row in rows:
            demande_id = row[0]
            if demande_id in seen_ids:
                print(f"⚠️ Doublon détecté pour la demande ID: {demande_id}")
                continue
            seen_ids.add(demande_id)
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
                "client_latitude": float(row[11]) if row[11] else None,
                "client_longitude": float(row[12]) if row[12] else None,
                "created_at": str(row[13]) if row[13] else None,
                "updated_at": str(row[14]) if row[14] else None,
                # Informations client
                "client_nom": row[15] if row[15] else None,
                "client_prenom": row[16] if row[16] else None,
                "client_email": row[17] if row[17] else None,
                "client_telephone": row[18] if row[18] else None,
                # Informations véhicule
                "marque": row[19] if row[19] else None,
                "modele": row[20] if row[20] else None,
                "immatriculation": row[21] if row[21] else None,
                # Informations service
                "service_nom": row[22] if row[22] else None,
                "service_description": row[23] if row[23] else None,
                "service_prix": float(row[24]) if row[24] else None,
                # Informations garage
                "nom_garage": row[25] if row[25] else None,
                "garage_latitude": float(row[26]) if row[26] else None,
                "garage_longitude": float(row[27]) if row[27] else None
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


@router.post("/")
def create_demande_prestation(
    demande_data: CreateDemandeRequest,
    db: Session = Depends(get_db)
):
    """Crée une nouvelle demande de prestation avec localisation et trouve automatiquement le garage le plus proche"""
    try:
        # Vérifier que le client existe
        client = db.query(Client).filter(Client.id == demande_data.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        
        # Vérifier que le véhicule existe
        vehicule = db.query(Vehicule).filter(Vehicule.id == demande_data.vehicule_id).first()
        if not vehicule:
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")
        
        # Vérifier que le service existe
        service = db.query(Service).filter(Service.id == demande_data.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        # Trouver le garage le plus proche
        nearest_garage = find_nearest_garage(
            demande_data.client_latitude,
            demande_data.client_longitude,
            db
        )
        
        # Créer la demande
        nouvelle_demande = DemandePrestation(
            client_id=demande_data.client_id,
            vehicule_id=demande_data.vehicule_id,
            service_id=demande_data.service_id,
            garage_id=nearest_garage.id if nearest_garage else None,
            date_demande=datetime.now(),
            date_souhaitee=demande_data.date_souhaitee,
            description_probleme=demande_data.description_probleme,
            statut='en_attente',
            client_latitude=demande_data.client_latitude,
            client_longitude=demande_data.client_longitude
        )
        
        db.add(nouvelle_demande)
        db.commit()
        db.refresh(nouvelle_demande)
        
        return {
            "success": True,
            "message": "Demande créée avec succès",
            "demande_id": nouvelle_demande.id,
            "garage_id": nouvelle_demande.garage_id,
            "garage_nom": nearest_garage.nom_garage if nearest_garage else None,
            "statut": nouvelle_demande.statut
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_str = str(e)
        print(f"Erreur lors de la création de la demande: {error_str}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création de la demande: {error_str}"
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
                dp.client_latitude,
                dp.client_longitude,
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
                g.nom_garage as garage_nom,
                g.latitude as garage_latitude,
                g.longitude as garage_longitude
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
            "client_latitude": float(row[11]) if row[11] else None,
            "client_longitude": float(row[12]) if row[12] else None,
            "created_at": str(row[13]) if row[13] else None,
            "updated_at": str(row[14]) if row[14] else None,
            "client_nom": row[15] if row[15] else None,
            "client_prenom": row[16] if row[16] else None,
            "client_email": row[17] if row[17] else None,
            "client_telephone": row[18] if row[18] else None,
            "marque": row[19] if row[19] else None,
            "modele": row[20] if row[20] else None,
            "immatriculation": row[21] if row[21] else None,
            "service_nom": row[22] if row[22] else None,
            "service_description": row[23] if row[23] else None,
            "service_prix": float(row[24]) if row[24] else None,
            "nom_garage": row[25] if row[25] else None,
            "garage_latitude": float(row[26]) if row[26] else None,
            "garage_longitude": float(row[27]) if row[27] else None
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

