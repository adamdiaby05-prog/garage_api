Write-Host "Démarrage de l'API FastAPI..." -ForegroundColor Green
Write-Host ""

# Vérifier Python
Write-Host "Vérification de Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python n'est pas trouvé. Veuillez installer Python." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installation des dépendances si nécessaire..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Démarrage du serveur sur http://localhost:8000" -ForegroundColor Green
Write-Host "Vous pouvez tester l'API sur http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

python main.py

