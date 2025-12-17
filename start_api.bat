@echo off
echo Demarrage de l'API FastAPI...
echo.
echo Verification de l'environnement...
py --version
echo.
echo Installation des dependances si necessaire...
py -m pip install -r requirements.txt
echo.
echo Demarrage du serveur sur http://localhost:8000
echo Vous pouvez tester l'API sur http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.
py main.py
pause

