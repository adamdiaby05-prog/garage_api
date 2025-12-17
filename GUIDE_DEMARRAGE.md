# Guide de Démarrage Complet

## Pour corriger l'erreur 500 lors de la connexion

L'erreur 500 signifie généralement que l'API ne peut pas se connecter à la base de données MySQL.

### Étapes à suivre dans l'ordre :

#### 1. Démarrer XAMPP/MySQL
- Ouvrez XAMPP Control Panel
- Démarrez le service **MySQL**
- Vérifiez que le port 3306 est actif (icône verte)

#### 2. Vérifier/Créer la base de données
- Ouvrez phpMyAdmin : `http://localhost/phpmyadmin`
- Vérifiez que la base de données `garage_db` existe
- Si elle n'existe pas, créez-la :
  ```sql
  CREATE DATABASE garage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

#### 3. Créer la table utilisateurs
Exécutez le script SQL dans phpMyAdmin :
- Ouvrez `create_users_table.sql`
- Copiez le contenu
- Collez dans l'onglet SQL de phpMyAdmin
- Exécutez

Ou utilisez Python :
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py check_database.py
```

#### 4. Démarrer l'API FastAPI
```powershell
cd C:\Users\ROG\Documents\garage\garage-Api
py main.py
```

Ou utilisez le script :
```powershell
.\start_api.bat
```

#### 5. Vérifier que tout fonctionne
- Testez l'API : `http://localhost:8000/docs`
- Testez la santé : `http://localhost:8000/health`
- Essayez de vous connecter dans l'application mobile

### Ordre de démarrage recommandé :
1. ✅ XAMPP (MySQL)
2. ✅ Base de données créée
3. ✅ Table utilisateurs créée
4. ✅ API FastAPI démarrée
5. ✅ Application Flutter

### Messages d'erreur courants :

**"Can't connect to MySQL"**
→ XAMPP/MySQL n'est pas démarré

**"Table doesn't exist"**
→ La table utilisateurs n'a pas été créée

**"TimeoutException"**
→ L'API n'est pas démarrée

**"Erreur 500"**
→ Vérifiez les logs de l'API dans le terminal

