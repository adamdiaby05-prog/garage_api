FROM python:3.11-slim

# Désactiver les .pyc et activer le flush des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dossier de travail
WORKDIR /app

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'API
COPY . /app

# Port de l'API (doit correspondre à API_PORT)
EXPOSE 8000

# Commande de démarrage FastAPI pour Dokploy
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


