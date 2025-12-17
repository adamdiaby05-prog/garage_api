# Guide de Demarrage Rapide

## Installation

1. **Installer les dependances** :
```powershell
cd garage-Api
py -m pip install -r requirements.txt
```

## Configuration

2. **Creer le fichier .env** :
   - Copiez `env.example.txt` en `.env`
   - Modifiez les parametres selon votre configuration MySQL

Exemple de `.env` :
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=garage_db
```

## Test de connexion

3. **Tester la connexion a la base de donnees** :
```powershell
py test_connection.py
```

## Demarrage de l'API

4. **Demarrer l'API** :

**Option 1 - Avec le script** :
```powershell
.\start.bat
```

**Option 2 - Directement avec Python** :
```powershell
py main.py
```

**Option 3 - Avec uvicorn** :
```powershell
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Acceder a l'API

Une fois demarree, l'API est accessible sur :
- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

## Endpoints disponibles

### Clients
- `GET /clients/` - Liste des clients
- `GET /clients/{id}` - Details d'un client
- `POST /clients/` - Creer un client
- `PUT /clients/{id}` - Modifier un client
- `DELETE /clients/{id}` - Supprimer un client

### Vehicules
- `GET /vehicules/` - Liste des vehicules
- `GET /vehicules/{id}` - Details d'un vehicule
- `POST /vehicules/` - Creer un vehicule
- `PUT /vehicules/{id}` - Modifier un vehicule
- `DELETE /vehicules/{id}` - Supprimer un vehicule

### Reparations
- `GET /reparations/` - Liste des reparations
- `GET /reparations/{id}` - Details d'une reparation
- `POST /reparations/` - Creer une reparation
- `PUT /reparations/{id}` - Modifier une reparation
- `DELETE /reparations/{id}` - Supprimer une reparation

### Services
- `GET /services/` - Liste des services
- `GET /services/{id}` - Details d'un service
- `POST /services/` - Creer un service
- `PUT /services/{id}` - Modifier un service
- `DELETE /services/{id}` - Supprimer un service

### Pieces
- `GET /pieces/` - Liste des pieces
- `GET /pieces/{id}` - Details d'une piece
- `POST /pieces/` - Creer une piece
- `PUT /pieces/{id}` - Modifier une piece
- `DELETE /pieces/{id}` - Supprimer une piece
- `GET /pieces/stock/critique` - Pieces en stock critique

### Employes
- `GET /employes/` - Liste des employes
- `GET /employes/{id}` - Details d'un employe
- `POST /employes/` - Creer un employe
- `PUT /employes/{id}` - Modifier un employe
- `DELETE /employes/{id}` - Supprimer un employe

### Factures
- `GET /factures/` - Liste des factures
- `GET /factures/{id}` - Details d'une facture
- `POST /factures/` - Creer une facture
- `PUT /factures/{id}` - Modifier une facture
- `DELETE /factures/{id}` - Supprimer une facture

### Rendez-vous
- `GET /rendez-vous/` - Liste des rendez-vous
- `GET /rendez-vous/{id}` - Details d'un rendez-vous
- `GET /rendez-vous/aujourdhui/liste` - Rendez-vous du jour
- `POST /rendez-vous/` - Creer un rendez-vous
- `PUT /rendez-vous/{id}` - Modifier un rendez-vous
- `DELETE /rendez-vous/{id}` - Supprimer un rendez-vous

## Exemple d'utilisation

### Creer un client avec curl
```bash
curl -X POST "http://localhost:8000/clients/" ^
  -H "Content-Type: application/json" ^
  -d "{\"nom\": \"Dupont\", \"prenom\": \"Jean\", \"telephone\": \"0123456789\"}"
```

### Recuperer la liste des clients
```bash
curl http://localhost:8000/clients/
```

## Notes importantes

- Sur Windows, utilisez `py` au lieu de `python` ou `pip`
- Assurez-vous que MySQL/MariaDB est demarre
- La base de donnees `garage_db` doit exister
- Les identifiants dans `.env` doivent etre corrects

