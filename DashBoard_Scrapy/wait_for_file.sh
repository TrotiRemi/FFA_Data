#!/bin/bash

FILE="/app/Docker_results_laver.csv"

echo "En attente de la création du fichier $FILE ..."
while [ ! -f "$FILE" ]; do
    sleep 2
done

echo "Fichier trouvé ! Lancement du dashboard..."
exec "$@"
