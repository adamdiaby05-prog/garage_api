from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from config import settings
from database import engine, Base
from routers import (
    clients,
    vehicules,
    reparations,
    services,
    pieces,
    employes,
    factures,
    rendez_vous,
    garages
)
from routers import auth

# Créer les tables si elles n'existent pas
from database import Base
try:
    from models_auth import Utilisateur
    print("Création/vérification des tables de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées/vérifiées avec succès")
except Exception as e:
    print(f"Attention: Erreur lors de la création des tables: {e}")
    print("Assurez-vous que la base de données est accessible et que les tables existent")

# Créer l'application FastAPI
app = FastAPI(
    title="Garage Management API",
    description="API REST pour la gestion d'un garage automobile",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(vehicules.router)
app.include_router(reparations.router)
app.include_router(services.router)
app.include_router(pieces.router)
app.include_router(employes.router)
app.include_router(factures.router)
app.include_router(rendez_vous.router)
app.include_router(garages.router)


@app.get("/")
def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Bienvenue sur l'API de gestion de garage",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Vérification de l'état de l'API et de la base de données"""
    from database import engine
    from config import settings
    
    try:
        # Tester la connexion à la base de données
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "db_host": settings.DB_HOST,
            "db_name": settings.DB_NAME,
            "api_version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "db_host": settings.DB_HOST,
            "db_name": settings.DB_NAME
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

