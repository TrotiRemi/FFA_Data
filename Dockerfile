FROM python:3.12.6

# Définir le répertoire de travail
WORKDIR /app

# Copier tout le projet dans l'image
COPY . /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Donner les permissions au script d'attente
RUN chmod +x wait_for_file.sh

# Commande par défaut
CMD ["bash"]
