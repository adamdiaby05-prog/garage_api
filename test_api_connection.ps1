Write-Host "Test de connexion à l'API..." -ForegroundColor Yellow
Write-Host ""

# Test de connexion à l'API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] L'API répond sur http://localhost:8000" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "Réponse: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "[ERREUR] L'API ne répond pas sur http://localhost:8000" -ForegroundColor Red
    Write-Host "Message d'erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions possibles:" -ForegroundColor Yellow
    Write-Host "1. Démarrez l'API avec: py main.py" -ForegroundColor White
    Write-Host "2. Vérifiez que le port 8000 n'est pas utilisé par un autre programme" -ForegroundColor White
    Write-Host "3. Vérifiez que MySQL/XAMPP est démarré" -ForegroundColor White
}

Write-Host ""
Write-Host "Test de connexion à l'API depuis l'émulateur (10.0.2.2:8000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://10.0.2.2:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] L'API est accessible depuis l'émulateur" -ForegroundColor Green
} catch {
    Write-Host "[INFO] 10.0.2.2 n'est accessible que depuis l'émulateur Android" -ForegroundColor Yellow
}

