# Configuration finale pour Dokploy - Résolution erreur 502 Bad Gateway

## 🔧 Variables d'environnement à configurer dans Dokploy

Dans l'interface Dokploy, pour votre application API (`garage-api-kvcuau`), allez dans la section **Environment** et ajoutez les variables suivantes :

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

## 📋 Étapes de configuration

### 1. Créer la base de données `garage_db`

La base de données doit être créée avant que l'API puisse fonctionner. Vous avez plusieurs options :

#### Option A : Via l'interface SQL de Dokploy (Recommandé)

1. Accédez à votre base de données `garage-database-8te5zx` dans Dokploy
2. Ouvrez l'interface SQL ou le terminal
3. Exécutez la commande suivante :

```sql
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. Accordez les permissions à l'utilisateur `mysql` :

```sql
GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;
```

#### Option B : Utiliser le script SQL fourni

Exécutez le fichier `create_database.sql` via l'interface SQL de Dokploy.

#### Option C : Utiliser le script Python d'initialisation

Si vous avez accès au conteneur de l'API, vous pouvez exécuter :

```bash
python init_database.py
```

### 2. Configurer les variables d'environnement

1. Dans Dokploy, allez dans votre application API (`garage-api-kvcuau`)
2. Ouvrez la section **Environment**
3. Ajoutez toutes les variables listées ci-dessus
4. **Important** : Sauvegardez les modifications

### 3. Redéployer l'application

1. Dans Dokploy, allez dans la section **Deployments**
2. Cliquez sur **Redeploy** ou **Deploy**
3. Attendez que le déploiement se termine
4. Vérifiez les logs pour confirmer que la connexion à la base de données réussit

### 4. Vérifier que tout fonctionne

1. Testez l'endpoint de santé : `http://garage-api-kvcuau-2f1ce1-213-199-48-58.traefik.me/health`
2. Vous devriez recevoir une réponse comme :

```json
{
  "status": "healthy",
  "database": "connected",
  "db_host": "garage-database-8te5zx",
  "db_name": "garage_db",
  "api_version": "1.0.0"
}
```

## 🔍 Dépannage

### Erreur 502 Bad Gateway

Si vous recevez toujours une erreur 502 :

1. **Vérifiez les logs de l'API** dans Dokploy (section **Logs**)
   - Cherchez les messages de connexion à la base de données
   - Vérifiez s'il y a des erreurs de connexion

2. **Vérifiez les variables d'environnement**
   - Assurez-vous que toutes les variables sont correctement configurées
   - Vérifiez qu'il n'y a pas d'espaces supplémentaires
   - Vérifiez que les valeurs sont exactes (sensible à la casse)

3. **Vérifiez que la base de données existe**
   - Connectez-vous à MySQL et exécutez : `SHOW DATABASES;`
   - Vous devriez voir `garage_db` dans la liste

4. **Vérifiez les permissions**
   - Exécutez : `SHOW GRANTS FOR 'mysql'@'%';`
   - Vous devriez voir les permissions sur `garage_db.*`

5. **Vérifiez que l'API est démarrée**
   - Dans les logs, vous devriez voir : `✅ Connexion à la base de données réussie`
   - Si vous voyez des erreurs, notez-les et consultez la section ci-dessous

### Erreurs de connexion courantes

#### "Access denied for user 'mysql'@% to database 'garage_db'"

**Solution** : L'utilisateur `mysql` n'a pas les permissions sur la base `garage_db`.

Exécutez en tant que root :
```sql
GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;
```

#### "Can't connect to MySQL server"

**Solution** : Vérifiez que :
- Le host `garage-database-8te5zx` est correct
- Le port `3306` est correct
- La base de données est démarrée dans Dokploy

#### "Unknown database 'garage_db'"

**Solution** : Créez la base de données :
```sql
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📝 Informations de connexion

### Base de données interne (dans Dokploy)
- **Host** : `garage-database-8te5zx`
- **Port** : `3306`
- **User** : `mysql`
- **Password** : `gt7yxk0c69yn90rs`
- **Database** : `garage_db`
- **URL de connexion** : `mysql://mysql:gt7yxk0c69yn90rs@garage-database-8te5zx:3306/garage_db`

### Base de données externe (depuis Internet)
- **Host** : `213.199.48.58`
- **Port** : `3306`
- **User** : `mysql`
- **Password** : `gt7yxk0c69yn90rs`
- **Database** : `garage_db`
- **URL de connexion** : `mysql://mysql:gt7yxk0c69yn90rs@213.199.48.58:3306/garage_db`

⚠️ **Note** : L'API doit utiliser le host interne (`garage-database-8te5zx`) car elle est déployée dans le même environnement Dokploy.

## ✅ Checklist de vérification

- [ ] Base de données `garage_db` créée
- [ ] Permissions accordées à l'utilisateur `mysql`
- [ ] Variables d'environnement configurées dans Dokploy
- [ ] Application redéployée
- [ ] Logs montrent une connexion réussie
- [ ] Endpoint `/health` retourne `"status": "healthy"`
- [ ] L'application mobile peut se connecter à l'API

## 🚀 Après la configuration

Une fois que tout est configuré :

1. L'API devrait démarrer automatiquement
2. Les tables seront créées automatiquement au premier démarrage
3. Vous pouvez accéder à la documentation de l'API à : `http://garage-api-kvcuau-2f1ce1-213-199-48-58.traefik.me/docs`
4. L'application mobile devrait pouvoir se connecter

## 📞 Support

Si vous rencontrez toujours des problèmes après avoir suivi ce guide :

1. Vérifiez les logs de l'API dans Dokploy
2. Vérifiez les logs de la base de données
3. Testez la connexion manuellement avec les credentials
4. Vérifiez que le port 8000 est correctement configuré dans Dokploy

