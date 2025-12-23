# Résolution de l'erreur "Access denied for user 'mysql'@% to database 'garage_db'"

## Problème

L'erreur `(1044, 'Access denied for user 'mysql'@% to database 'garage_db')` indique que l'utilisateur MySQL `mysql` n'a pas les permissions nécessaires pour accéder à la base de données `garage_db`.

## Solutions

### Solution 1 : Donner les permissions (Recommandé)

1. **Connectez-vous à la base de données Dokploy en tant qu'administrateur (root)**
   - Utilisez le mot de passe root : `sntsksrmu3w2dgxy`
   - Via l'interface SQL de Dokploy ou un client MySQL

2. **Exécutez les commandes SQL suivantes :**

```sql
-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Donner toutes les permissions à l'utilisateur 'mysql'
GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;
```

3. **Vérifiez les permissions :**
```sql
SHOW GRANTS FOR 'mysql'@'%';
```

### Solution 2 : Utiliser la base 'mysql' par défaut (Temporaire)

Si vous ne pouvez pas modifier les permissions, vous pouvez temporairement utiliser la base `mysql` :

1. **Dans Dokploy, modifiez la variable d'environnement :**
   ```
   DB_NAME=mysql
   ```

2. **Redéployez l'API**

⚠️ **Note** : Ce n'est pas recommandé car la base `mysql` est utilisée par MySQL lui-même. Créez plutôt une base dédiée.

### Solution 3 : Créer un utilisateur dédié (Optionnel)

Si vous préférez créer un utilisateur spécifique pour l'application :

```sql
-- Créer un nouvel utilisateur
CREATE USER 'garage_user'@'%' IDENTIFIED BY 'votre_mot_de_passe_securise';

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Donner les permissions
GRANT ALL PRIVILEGES ON garage_db.* TO 'garage_user'@'%';
FLUSH PRIVILEGES;
```

Puis mettez à jour les variables d'environnement :
```
DB_USER=garage_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_NAME=garage_db
```

## Vérification

Après avoir appliqué les permissions, testez la connexion :

1. **Redéployez l'API** dans Dokploy
2. **Testez l'endpoint** `/health` qui devrait retourner :
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "db_host": "garage-database-8te5zx",
     "db_name": "garage_db"
   }
   ```
3. **Essayez de vous connecter** sur l'application mobile

## Fichiers utiles

- `fix_database_permissions.sql` - Script SQL pour corriger les permissions
- `create_database.sql` - Script pour créer la base de données
- `test_dokploy_connection.py` - Script Python pour tester la connexion

