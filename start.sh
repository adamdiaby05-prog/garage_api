#!/bin/bash

echo "Démarrage de l'API Garage..."
echo ""

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "ATTENTION: Le fichier .env n'existe pas!"
    echo "Veillez créer un fichier .env avec vos paramètres de connexion."
    echo ""
    echo "Exemple de contenu pour .env:"
    echo "DB_HOST=127.0.0.1"
    echo "DB_PORT=3306"
    echo "DB_USER=root"
    echo "DB_PASSWORD="
    echo "DB_NAME=garage_db"
    echo "API_HOST=0.0.0.0"
    echo "API_PORT=8000"
    echo "DEBUG=True"
    echo ""
    exit 1
fi

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Démarrer l'API
python main.py

