# Dépannage Rapide - Connexion API depuis l'Émulateur

## ✅ L'API fonctionne !
L'API répond correctement sur `http://localhost:8000`. Le problème vient de la connexion depuis l'émulateur Android.

## Solutions (dans l'ordre)

### Solution 1: Vérifier le Firewall Windows ⚠️ (Le plus fréquent)

Le pare-feu Windows bloque souvent les connexions depuis l'émulateur.

**Étapes:**
1. Ouvrez "Pare-feu Windows Defender" (recherchez dans le menu Démarrer)
2. Cliquez sur "Autoriser une application via le pare-feu"
3. Cliquez sur "Modifier les paramètres" (en haut à droite)
4. Cherchez "Python" dans la liste
5. ✅ Cochez les cases "Privé" et "Public" pour Python
6. Si Python n'est pas dans la liste :
   - Cliquez sur "Autoriser une autre application"
   - Cliquez sur "Parcourir"
   - Allez dans `C:\Users\ROG\AppData\Local\Programs\Python\Python313\`
   - Sélectionnez `python.exe`
   - Cliquez sur "Ajouter"
   - ✅ Cochez "Privé" et "Public"

**Redémarrer l'API après avoir modifié le firewall:**
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py main.py
```

### Solution 2: Vérifier que l'API écoute sur toutes les interfaces

Vérifiez dans `config.py`:
```python
API_HOST: str = "0.0.0.0"  # Doit être 0.0.0.0, pas 127.0.0.1
```

**Vérifier avec netstat:**
```powershell
netstat -ano | findstr :8000
```

Vous devriez voir:
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```

Si vous voyez `127.0.0.1:8000`, redémarrez l'API.

### Solution 3: Redémarrer l'Émulateur Android

Parfois, redémarrer l'émulateur résout les problèmes de réseau.

1. Fermez l'émulateur
2. Redémarrez-le
3. Réessayez de vous connecter

### Solution 4: Utiliser l'IP de votre Machine

Si `10.0.2.2` ne fonctionne toujours pas:

1. Trouvez l'IP de votre machine:
   ```powershell
   ipconfig
   ```
   Cherchez "Adresse IPv4" (ex: `192.168.1.100`)

2. Modifiez `garage-mobile/lib/config/api_config.dart`:
   ```dart
   static const String baseUrl = 'http://192.168.1.100:8000';
   ```

3. Redémarrez l'application Flutter

### Solution 5: Vérifier que MySQL/XAMPP est Démarré

L'API a besoin de MySQL pour fonctionner:

1. Ouvrez XAMPP Control Panel
2. ✅ Vérifiez que MySQL est démarré (icône verte)
3. Si ce n'est pas le cas, cliquez sur "Start"

## Test Rapide

**Test 1: L'API fonctionne sur localhost ?**
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py verifier_api.py
```
✅ Devrait afficher "[SUCCÈS] L'API fonctionne correctement!"

**Test 2: L'API écoute sur toutes les interfaces ?**
```powershell
netstat -ano | findstr :8000
```
✅ Devrait afficher `0.0.0.0:8000`

**Test 3: Le firewall autorise Python ?**
- Vérifiez dans "Pare-feu Windows Defender"
- Python doit être coché pour "Privé" et "Public"

## Ordre de Vérification Recommandé

1. ✅ API démarrée avec `py main.py`
2. ✅ MySQL/XAMPP démarré
3. ✅ Firewall autorise Python (Solution 1)
4. ✅ API écoute sur `0.0.0.0:8000` (Solution 2)
5. ✅ Émulateur redémarré (Solution 3)
6. ✅ Utiliser l'IP de la machine si nécessaire (Solution 4)

## Commandes Utiles

**Vérifier l'API:**
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py verifier_api.py
```

**Vérifier le port:**
```powershell
netstat -ano | findstr :8000
```

**Redémarrer l'API:**
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py main.py
```

## Besoin d'Aide ?

Si rien ne fonctionne, vérifiez les logs de l'API dans le terminal où elle est démarrée. Les erreurs seront affichées là-bas.

