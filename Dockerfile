# Utiliser l'image officielle Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement requirements.txt pour installer les dépendances
COPY requirements.txt /app/

# Installer les dépendances Python (étape mise en cache)
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . /app/

# Assurez-vous que MongoDB est accessible dans Scrapy
ENV MONGO_URI=mongodb://mongodb:27017/
ENV MONGO_DATABASE=athle_database
ENV MONGO_COLLECTION=results

# Commande de démarrage par défaut
CMD ["bash"]
