# Solution pour les Problèmes de Connexion avec l'Émulateur Android

## Problème
L'application Flutter dans l'émulateur Android ne peut pas se connecter à l'API FastAPI qui fonctionne sur `localhost:8000`.

## Solution

### 1. Vérifier que l'API est démarrée

L'API doit écouter sur `0.0.0.0:8000` (toutes les interfaces) et non seulement sur `127.0.0.1:8000`.

**Vérifier la configuration dans `config.py`:**
```python
API_HOST: str = "0.0.0.0"  # Doit être 0.0.0.0, pas 127.0.0.1
API_PORT: int = 8000
```

**Redémarrer l'API:**
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py main.py
```

### 2. Vérifier le Firewall Windows

Le firewall Windows peut bloquer les connexions depuis l'émulateur.

**Solution: Autoriser Python dans le Firewall**

1. Ouvrez "Pare-feu Windows Defender" dans les Paramètres
2. Cliquez sur "Autoriser une application via le pare-feu"
3. Cliquez sur "Modifier les paramètres"
4. Trouvez "Python" dans la liste et cochez les cases "Privé" et "Public"
5. Si Python n'est pas dans la liste, cliquez sur "Autoriser une autre application" et ajoutez Python

**Ou désactiver temporairement le firewall pour tester:**
- Ouvrez "Pare-feu Windows Defender"
- Cliquez sur "Activer ou désactiver le pare-feu Windows Defender"
- Désactivez temporairement pour tester (pas recommandé en production)

### 3. Vérifier l'URL dans l'Application Flutter

L'URL doit être correcte dans `lib/config/api_config.dart`:

```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

- `10.0.2.2` = adresse spéciale de l'émulateur Android pour accéder à `localhost` de la machine hôte
- Pour un appareil physique, utilisez l'IP de votre machine Windows

### 4. Tester la Connexion

**Depuis votre navigateur sur la machine Windows:**
```
http://localhost:8000/health
```

**Depuis l'émulateur (via adb):**
```powershell
adb shell
curl http://10.0.2.2:8000/health
```

### 5. Vérifier que le Port 8000 est Ouvert

```powershell
netstat -ano | findstr :8000
```

Vous devriez voir:
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```

Si vous voyez `127.0.0.1:8000` au lieu de `0.0.0.0:8000`, l'API n'écoute que sur localhost.

### 6. Utiliser l'IP de votre Machine (Alternative)

Si `10.0.2.2` ne fonctionne pas, trouvez l'IP de votre machine:

```powershell
ipconfig
```

Cherchez l'adresse IPv4 (ex: `192.168.1.100`), puis dans `lib/config/api_config.dart`:

```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

**Note:** Pour que cela fonctionne, votre machine et l'émulateur doivent être sur le même réseau.

### 7. Redémarrer l'Émulateur

Parfois, redémarrer l'émulateur Android peut résoudre les problèmes de connexion réseau.

## Vérification Rapide

1. ✅ API démarrée avec `host=0.0.0.0`
2. ✅ Port 8000 accessible depuis localhost
3. ✅ Firewall autorise Python
4. ✅ URL correcte dans l'app (`10.0.2.2:8000`)
5. ✅ Émulateur redémarré si nécessaire

## Commandes Utiles

**Tester l'API:**
```powershell
py verifier_api.py
```

**Vérifier les processus Python:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

**Vérifier le port:**
```powershell
netstat -ano | findstr :8000
```

