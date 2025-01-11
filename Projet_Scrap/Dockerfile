# Utiliser une version stable de Python
FROM python:3.12.6 

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier tous les fichiers du projet dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande par défaut pour exécuter le script
CMD ["python", "Extract_Course_Mongo.py"]
