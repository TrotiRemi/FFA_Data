#!/bin/bash

FILE="/shared/Docker_results_laver.csv"

echo "Vérification des fichiers dans /shared au démarrage :"
ls -la /shared

# Boucle pour vérifier l'existence du fichier toutes les 10 secondes
while true; do
    if [ -f "$FILE" ]; then
        echo "Fichier trouvé : $FILE"
        echo "Lancement du dashboard..."
        exec "$@"  # Lancer la commande passée en argument
        break
    else
        echo "Fichier non trouvé. Nouvelle vérification dans 10 secondes..."
        sleep 10
    fi
done
