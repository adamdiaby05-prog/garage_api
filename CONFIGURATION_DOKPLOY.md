# Configuration de la base de données Dokploy

## Informations de connexion

D'après votre configuration Dokploy :

- **Host interne**: `garage-database-8te5zx`
- **Port**: `3306`
- **User**: `mysql`
- **Password**: `gt7yxk0c69yn90rs`
- **Database Name**: `mysql` (ou `garage_db` si vous l'avez créée)

## Configuration dans Dokploy

### 1. Variables d'environnement à configurer

Dans l'interface Dokploy, pour votre application API (`garage-api-kvcuau`), configurez les variables d'environnement suivantes dans la section **Environment** :

```env
DB_HOST=garage-database-8te5zx
DB_PORT=3306
DB_USER=mysql
DB_PASSWORD=gt7yxk0c69yn90rs
DB_NAME=garage_db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### 2. Créer la base de données `garage_db`

Si la base de données `garage_db` n'existe pas encore, vous devez la créer. Vous pouvez :

#### Option A : Via l'interface Dokploy (si disponible)
- Accédez à la base de données dans Dokploy
- Utilisez l'interface SQL pour créer la base :
```sql
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Option B : Via un script SQL
Exécutez le script `create_users_table.sql` qui créera automatiquement la base si elle n'existe pas.

#### Option C : Modifier temporairement DB_NAME
Si vous voulez utiliser la base `mysql` par défaut (non recommandé), changez :
```env
DB_NAME=mysql
```

### 3. Vérification de la connexion

Une fois les variables configurées, l'API devrait se connecter automatiquement à la base de données Dokploy.

Pour vérifier :
1. Redéployez l'application API
2. Vérifiez les logs pour voir si la connexion réussit
3. Testez l'endpoint `/health` qui devrait retourner `{"status": "healthy", "database": "connected"}`

## Structure de l'URL de connexion

L'API construit automatiquement l'URL de connexion :
```
mysql+pymysql://mysql:gt7yxk0c69yn90rs@garage-database-8te5zx:3306/garage_db?charset=utf8mb4
```

## Important

⚠️ **Sécurité** : Ne commitez JAMAIS le fichier `.env` avec les mots de passe dans Git. Les variables d'environnement doivent être configurées uniquement dans Dokploy.

## Migration depuis localhost

Si vous migrez depuis une base de données locale :
1. Exportez vos données locales
2. Importez-les dans la base Dokploy
3. Mettez à jour les variables d'environnement
4. Redéployez l'API



