from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Configuration de la base de données
    # Valeurs par défaut pour Dokploy (peuvent être surchargées par variables d'environnement)
    DB_HOST: str = os.getenv("DB_HOST", "garage-database-8te5zx")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "mysql")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "gt7yxk0c69yn90rs")
    DB_NAME: str = os.getenv("DB_NAME", "garage_db")
    
    # Configuration de l'API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @property
    def database_url(self) -> str:
        """Construit l'URL de connexion à la base de données"""
        # Encoder le mot de passe pour les caractères spéciaux dans l'URL
        from urllib.parse import quote_plus
        password_encoded = quote_plus(self.DB_PASSWORD)
        return f"mysql+pymysql://{self.DB_USER}:{password_encoded}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Permettre de lire depuis les variables d'environnement système
        env_file_encoding = 'utf-8'


settings = Settings()

# Afficher la configuration (sans le mot de passe) pour le débogage
print(f"🔧 Configuration de la base de données:")
print(f"   Host: {settings.DB_HOST}")
print(f"   Port: {settings.DB_PORT}")
print(f"   User: {settings.DB_USER}")
print(f"   Database: {settings.DB_NAME}")
print(f"   API Host: {settings.API_HOST}")
print(f"   API Port: {settings.API_PORT}")
print(f"   Debug: {settings.DEBUG}")

