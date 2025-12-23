-- Script pour créer la base de données garage_db sur Dokploy
-- Exécutez ce script via l'interface SQL de Dokploy ou via une connexion MySQL

-- Créer la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Utiliser la base de données
USE garage_db;

-- La table utilisateurs sera créée automatiquement par l'API via SQLAlchemy
-- Mais vous pouvez aussi l'exécuter manuellement si nécessaire
-- Voir create_users_table.sql



