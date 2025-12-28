# Comment exécuter le script SQL sur Dokploy

## 🎯 Objectif

Ajouter les colonnes de localisation (`client_latitude`, `client_longitude` pour `demandes_prestations` et `latitude`, `longitude` pour `garages`) dans la base de données MySQL.

## ✅ Méthode recommandée : Script Python (dans le conteneur de l'API)

Puisque `mysql` n'est pas disponible dans le conteneur de l'API, utilisez le script Python :

### Dans le terminal Docker de l'API (`garage-api-kvcuau`)

```bash
# Naviguer vers le répertoire de l'application
cd /app

# Exécuter le script Python
python add_location_columns_script.py
```

Le script :
- ✅ Se connecte automatiquement à la base de données
- ✅ Ajoute les colonnes nécessaires
- ✅ Crée les index pour améliorer les performances
- ✅ Gère les erreurs si les colonnes existent déjà

---

## 📋 Alternative : Via le terminal Docker de la base de données

Si vous avez accès au terminal Docker de la base de données MySQL (`garage-database-8te5zx`) :

### Étape 1 : Accéder au terminal Docker de la base de données

1. Dans Dokploy, allez dans votre base de données `garage-database-8te5zx`
2. Ouvrez l'onglet **Terminal** ou **Logs** > **Docker Terminal**
3. Sélectionnez **Bash** comme shell

### Étape 2 : Se connecter à MySQL

```bash
mysql -u root -p
```

Quand il demande le mot de passe, entrez :
```
sntsksrmu3w2dgxy
```

### Étape 3 : Sélectionner la base de données

```sql
USE garage_db;
```

### Étape 4 : Exécuter les commandes SQL

```sql
ALTER TABLE demandes_prestations ADD COLUMN client_latitude DECIMAL(10, 8) NULL;
ALTER TABLE demandes_prestations ADD COLUMN client_longitude DECIMAL(11, 8) NULL;
ALTER TABLE garages ADD COLUMN latitude DECIMAL(10, 8) NULL;
ALTER TABLE garages ADD COLUMN longitude DECIMAL(11, 8) NULL;
CREATE INDEX idx_demandes_client_location ON demandes_prestations(client_latitude, client_longitude);
CREATE INDEX idx_garages_location ON garages(latitude, longitude);
```

### Étape 5 : Vérifier

```sql
DESCRIBE demandes_prestations;
DESCRIBE garages;
EXIT;
```

---

## ✅ Vérification après exécution

Pour vérifier que les colonnes ont été ajoutées via Python :

```bash
cd /app
python -c "
from database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('DESCRIBE demandes_prestations'))
    cols = [row[0] for row in result]
    print('Colonnes demandes_prestations:', [c for c in cols if 'latitude' in c or 'longitude' in c])
    
    result = conn.execute(text('DESCRIBE garages'))
    cols = [row[0] for row in result]
    print('Colonnes garages:', [c for c in cols if 'latitude' in c or 'longitude' in c])
"
```

---

## 📝 Informations de connexion Dokploy

- **Host interne** : `garage-database-8te5zx`
- **Port** : `3306`
- **User root** : `root`
- **Root Password** : `sntsksrmu3w2dgxy`
- **User normal** : `mysql`
- **Password normal** : `gt7yxk0c69yn90rs`
- **Database** : `garage_db`
