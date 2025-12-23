# Correction du rôle utilisateur

## Problème

L'utilisateur `a@gmail.com` apparaît avec des rôles différents selon la plateforme :
- **Site web** : reconnu comme "garage"
- **App mobile** : reconnu comme "client"

Ils utilisent pourtant la même base de données.

## Cause probable

1. **Doublons dans la base de données** : Il peut y avoir plusieurs enregistrements avec le même email mais des rôles différents
2. **Rôle incorrect dans la base de données** : Le rôle stocké ne correspond pas au rôle attendu

## Solution

### Étape 1 : Vérifier l'utilisateur dans la base de données

```bash
python check_user_role.py check a@gmail.com
```

Cela affichera tous les utilisateurs avec cet email et leurs rôles.

### Étape 2 : Corriger le rôle si nécessaire

Si le rôle est incorrect, corrigez-le :

```bash
# Pour définir comme garage
python check_user_role.py fix a@gmail.com garage

# Pour définir comme client
python check_user_role.py fix a@gmail.com client

# Pour définir comme admin
python check_user_role.py fix a@gmail.com admin
```

### Étape 3 : Supprimer les doublons

S'il y a plusieurs utilisateurs avec le même email, supprimez les doublons (le plus récent sera conservé) :

```bash
python check_user_role.py remove-duplicates a@gmail.com
```

## Vérification via SQL direct

Vous pouvez aussi vérifier directement dans la base de données :

```sql
-- Vérifier tous les utilisateurs avec cet email
SELECT id, email, role, garage_id, nom_complet, created_at 
FROM utilisateurs 
WHERE email = 'a@gmail.com'
ORDER BY created_at DESC;

-- Mettre à jour le rôle (remplacer X par l'ID correct)
UPDATE utilisateurs 
SET role = 'garage' 
WHERE email = 'a@gmail.com' AND id = X;

-- Supprimer les doublons (garder le plus récent)
DELETE FROM utilisateurs 
WHERE email = 'a@gmail.com' 
AND id NOT IN (
    SELECT id FROM (
        SELECT id FROM utilisateurs 
        WHERE email = 'a@gmail.com' 
        ORDER BY created_at DESC 
        LIMIT 1
    ) AS temp
);
```

## Après correction

1. Redémarrez l'API si nécessaire
2. Déconnectez-vous et reconnectez-vous sur les deux plateformes
3. Vérifiez que le rôle est maintenant cohérent



