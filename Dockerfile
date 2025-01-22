# Utiliser l'image officielle Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app/

# Installer les dépendances Python
RUN pip install -r requirements.txt

# Assurez-vous que MongoDB est accessible dans Scrapy
ENV MONGO_URI=mongodb://mongodb:27017/
ENV MONGO_DATABASE=athle_database
ENV MONGO_COLLECTION=results

# Commande de démarrage par défaut
CMD ["bash"]
