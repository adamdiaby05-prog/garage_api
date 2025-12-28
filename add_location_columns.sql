-- Script pour ajouter les colonnes de localisation aux tables demandes_prestations et garages

-- Ajouter les colonnes de localisation à la table demandes_prestations
ALTER TABLE demandes_prestations 
ADD COLUMN IF NOT EXISTS client_latitude DECIMAL(10, 8) NULL,
ADD COLUMN IF NOT EXISTS client_longitude DECIMAL(11, 8) NULL;

-- Ajouter les colonnes de localisation à la table garages
ALTER TABLE garages 
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 8) NULL,
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11, 8) NULL;

-- Ajouter des index pour améliorer les performances des requêtes de recherche
CREATE INDEX IF NOT EXISTS idx_demandes_client_location ON demandes_prestations(client_latitude, client_longitude);
CREATE INDEX IF NOT EXISTS idx_garages_location ON garages(latitude, longitude);

