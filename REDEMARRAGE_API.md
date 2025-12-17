# 🔄 Redémarrage de l'API - Important

## Problème

L'erreur `Unknown column 'utilisateurs.nom_complet'` peut persister même après avoir corrigé la base de données si l'API n'a pas été redémarrée.

## Solution

L'API doit être **redémarrée** pour recharger le schéma de la base de données.

### Méthode 1 : Via PowerShell (Recommandé)

```powershell
cd C:\Users\ROG\Documents\garage\garage-Api

# Arrêter tous les processus Python
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# Attendre 2 secondes
Start-Sleep -Seconds 2

# Redémarrer l'API
python main.py
```

### Méthode 2 : Manuellement

1. **Trouvez la fenêtre de terminal où l'API tourne**
2. **Appuyez sur `Ctrl+C`** pour arrêter l'API
3. **Relancez l'API** :
   ```powershell
   cd C:\Users\ROG\Documents\garage\garage-Api
   python main.py
   ```

### Méthode 3 : Utiliser le script de démarrage

```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
.\start_api.ps1
```

## Vérification

Après le redémarrage, vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test

Testez la connexion dans l'application Flutter. L'erreur devrait avoir disparu !

## Note

Si l'erreur persiste après le redémarrage :
1. Vérifiez que MySQL/XAMPP est démarré
2. Exécutez `py force_reload_schema.py` pour vérifier le schéma
3. Vérifiez les logs de l'API pour d'autres erreurs


