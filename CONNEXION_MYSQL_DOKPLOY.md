# Comment se connecter à MySQL dans le conteneur Dokploy

## Méthode 1 : Via le terminal Docker (Recommandé)

1. **Dans le terminal Docker de Dokploy**, connectez-vous à MySQL avec l'utilisateur root :

```bash
mysql -u root -p
```

2. **Entrez le mot de passe root** quand demandé :
```
sntsksrmu3w2dgxy
```

3. **Une fois connecté à MySQL**, vous verrez le prompt `mysql>`. Exécutez alors les commandes SQL :

```sql
-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Donner toutes les permissions à l'utilisateur 'mysql'
GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- Vérifier les permissions
SHOW GRANTS FOR 'mysql'@'%';

-- Vérifier que la base existe
SHOW DATABASES;
```

4. **Quitter MySQL** :
```sql
EXIT;
```

## Méthode 2 : Exécuter directement depuis bash

Si vous préférez rester dans bash, vous pouvez exécuter MySQL en une ligne :

```bash
mysql -u root -psntsksrmu3w2dgxy -e "CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

```bash
mysql -u root -psntsksrmu3w2dgxy -e "GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%'; FLUSH PRIVILEGES;"
```

## Méthode 3 : Via un script SQL

1. **Créez un fichier SQL** avec les commandes (ou utilisez `fix_database_permissions.sql`)

2. **Exécutez-le** :
```bash
mysql -u root -psntsksrmu3w2dgxy < fix_database_permissions.sql
```

Ou si le fichier est dans le conteneur :
```bash
mysql -u root -psntsksrmu3w2dgxy < /chemin/vers/fix_database_permissions.sql
```

## Vérification

Après avoir exécuté les commandes, vérifiez :

```bash
mysql -u root -psntsksrmu3w2dgxy -e "SHOW DATABASES;"
```

Vous devriez voir `garage_db` dans la liste.

```bash
mysql -u root -psntsksrmu3w2dgxy -e "SHOW GRANTS FOR 'mysql'@'%';"
```

Vous devriez voir les permissions sur `garage_db.*`.

