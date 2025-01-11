#!/bin/bash

FILE="/shared/Docker_results_laver.csv"
TIMEOUT=${WAIT_TIMEOUT:-300} # Délai maximal en secondes (par défaut 300 secondes)
INTERVAL=10                  # Intervalle entre les vérifications
WAITED=0                     # Temps déjà attendu

echo "Commencement de la vérification du fichier : $FILE"
echo "Délai maximal d'attente : $TIMEOUT secondes"

# Vérifier l'existence du fichier toutes les $INTERVAL secondes
while true; do
    if [ -f "$FILE" ]; then
        echo "Fichier trouvé : $FILE"
        echo "Lancement de la commande..."
        exec "$@"  # Lancer la commande passée en argument
        break
    else
        echo "Fichier non trouvé. Nouvelle vérification dans $INTERVAL secondes..."
        sleep $INTERVAL
        WAITED=$((WAITED + INTERVAL))
        if [ $WAITED -ge $TIMEOUT ]; then
            echo "Erreur : délai maximal d'attente atteint ($TIMEOUT secondes)."
            exit 1
        fi
    fi
done
