-- Script pour corriger les permissions de la base de données sur Dokploy
-- Exécutez ce script en tant qu'administrateur (root) via l'interface SQL de Dokploy

-- Option 1: Donner toutes les permissions à l'utilisateur 'mysql' sur 'garage_db'
-- Si la base de données n'existe pas encore, créez-la d'abord
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Donner toutes les permissions à l'utilisateur 'mysql' sur 'garage_db'
GRANT ALL PRIVILEGES ON garage_db.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- Vérifier les permissions
SHOW GRANTS FOR 'mysql'@'%';

-- Option 2: Si vous préférez utiliser la base 'mysql' par défaut (non recommandé)
-- Vous pouvez changer DB_NAME dans les variables d'environnement à 'mysql'
-- Mais il est préférable de créer une base dédiée

