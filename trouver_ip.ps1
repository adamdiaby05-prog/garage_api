# Script pour trouver l'IP à utiliser dans l'application Flutter

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Recherche de l'IP pour l'application Flutter" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Obtenir toutes les adresses IP IPv4
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -notlike "127.*" -and 
    $_.IPAddress -notlike "169.254.*" -and
    $_.IPAddress -notlike "172.26.*"
} | Select-Object IPAddress, InterfaceAlias

Write-Host "Adresses IP disponibles sur votre machine :" -ForegroundColor Yellow
Write-Host ""

$wifiIp = $null
foreach ($ip in $ips) {
    $status = ""
    if ($ip.InterfaceAlias -like "*Wi-Fi*" -or $ip.InterfaceAlias -like "*WLAN*") {
        $status = " [RECOMMANDÉ - Wi-Fi]"
        $wifiIp = $ip.IPAddress
        Write-Host "  $($ip.IPAddress) - $($ip.InterfaceAlias)$status" -ForegroundColor Green
    } else {
        Write-Host "  $($ip.IPAddress) - $($ip.InterfaceAlias)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Configuration recommandée :" -ForegroundColor Yellow
Write-Host ""

if ($wifiIp) {
    Write-Host "IP Wi-Fi trouvée : $wifiIp" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dans garage-mobile/lib/config/api_config.dart, utilisez :" -ForegroundColor Cyan
    Write-Host "  static const String baseUrl = 'http://$wifiIp:8000';" -ForegroundColor White
} else {
    $firstIp = $ips[0].IPAddress
    Write-Host "Utilisez cette IP : $firstIp" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Dans garage-mobile/lib/config/api_config.dart, utilisez :" -ForegroundColor Cyan
    Write-Host "  static const String baseUrl = 'http://$firstIp:8000';" -ForegroundColor White
}

Write-Host ""
Write-Host "Pour l'émulateur Android, vous pouvez aussi essayer :" -ForegroundColor Yellow
Write-Host "  static const String baseUrl = 'http://10.0.2.2:8000';" -ForegroundColor Gray

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# Tester la connexion à l'API
Write-Host ""
Write-Host "Test de connexion à l'API..." -ForegroundColor Yellow

if ($wifiIp) {
    $testUrl = "http://$wifiIp:8000/health"
} else {
    $testUrl = "http://$($ips[0].IPAddress):8000/health"
}

try {
    $response = Invoke-WebRequest -Uri $testUrl -Method GET -TimeoutSec 3 -ErrorAction Stop
    Write-Host "[OK] L'API est accessible sur $testUrl" -ForegroundColor Green
} catch {
    Write-Host "[ATTENTION] L'API n'est pas accessible sur $testUrl" -ForegroundColor Red
    Write-Host "Assurez-vous que l'API est démarrée avec: py main.py" -ForegroundColor Yellow
}

Write-Host ""

