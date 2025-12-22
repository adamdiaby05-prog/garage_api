# Guide de déploiement sur Dokploy

## Configuration requise

### Variables d'environnement

Configurez les variables d'environnement suivantes dans Dokploy :

```
DB_HOST=votre_host_mysql
DB_PORT=3306
DB_USER=votre_utilisateur
DB_PASSWORD=votre_mot_de_passe
DB_NAME=garage_db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

### Configuration Dokploy

1. **Build Type**: Dockerfile
2. **Docker File**: Dockerfile
3. **Docker Context Path**: . (point)
4. **Port**: 8000

### Base de données

Assurez-vous que :
- La base de données MySQL est accessible depuis le conteneur
- Les tables sont créées (utilisez `create_users_table.sql` si nécessaire)
- Les variables d'environnement de connexion sont correctement configurées

### Déploiement

1. Poussez le code sur GitHub
2. Configurez les variables d'environnement dans Dokploy
3. Déployez l'application
4. Vérifiez les logs pour s'assurer que l'application démarre correctement

### Vérification

Une fois déployé, vous pouvez vérifier :
- `/` - Point d'entrée de l'API
- `/health` - Vérification de l'état
- `/docs` - Documentation Swagger
- `/redoc` - Documentation ReDoc

