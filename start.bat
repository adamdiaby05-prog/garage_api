@echo off
echo Démarrage de l'API Garage...
echo.

REM Vérifier si le fichier .env existe
if not exist .env (
    echo ATTENTION: Le fichier .env n'existe pas!
    echo Veuillez créer un fichier .env avec vos paramètres de connexion.
    echo.
    echo Exemple de contenu pour .env:
    echo DB_HOST=127.0.0.1
    echo DB_PORT=3306
    echo DB_USER=root
    echo DB_PASSWORD=
    echo DB_NAME=garage_db
    echo API_HOST=0.0.0.0
    echo API_PORT=8000
    echo DEBUG=True
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel si présent
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Démarrer l'API
python main.py

pause

