from pymongo import MongoClient

def check_data_count():
    try:
        # Connexion à MongoDB
        client = MongoClient("mongodb://mongodb:27017/")  # Adaptez si MongoDB est local
        db = client["athle_database"]
        collection = db["results"]

        # Vérifiez le nombre de documents
        count = collection.count_documents({})
        print(f"Nombre de documents dans la collection : {count}")
        return count >= 10000  # Retourne True si 500 données ou plus
    except Exception as e:
        print(f"Erreur lors de la vérification des données : {e}")
        return False
