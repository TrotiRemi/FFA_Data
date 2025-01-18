import json
import urllib.request

def extract_GeoJson(url) :
    try:
        with urllib.request.urlopen(url) as response:
            return(json.load(response))
    except Exception as e:
        print(f"Erreur lors de l'ouverture du fichier GeoJSON : {e}")
        return