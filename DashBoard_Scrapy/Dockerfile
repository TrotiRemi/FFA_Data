FROM python:3.12.6

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers source dans l'image
COPY . /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script d'attente et donner les permissions
COPY wait_for_file.sh /app/wait_for_file.sh
RUN chmod +x /app/wait_for_file.sh

# Commande de démarrage
CMD ["/bin/sh", "/app/wait_for_file.sh", "python3", "main.py"]
