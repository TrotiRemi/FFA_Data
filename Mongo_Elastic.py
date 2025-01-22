from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
import os

# Paramètres MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "athle_database")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "results")

# Paramètres Elasticsearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "athle_results")

def Mongo_Elastic():
    """
    Synchronise les données de MongoDB vers Elasticsearch.
    """
    # Connexion à MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[MONGO_COLLECTION]

    # Connexion à Elasticsearch
    es = Elasticsearch(hosts=[ELASTICSEARCH_URL])

    # Vérification si l'index existe dans Elasticsearch, sinon création
    if not es.indices.exists(index=ELASTICSEARCH_INDEX):
        es.indices.create(
            index=ELASTICSEARCH_INDEX,
            body={
                "mappings": {
                    "properties": {
                        "competition_name": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "distance": {"type": "float"},
                        "Minute_Time": {"type": "float"},
                        "athlete": {"type": "text"},
                        "club": {"type": "text"},
                        "category": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "department": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "competition_date": {"type": "date", "format": "yyyy-MM-dd"},
                        "vitesse": {"type": "float"},
                        "type": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                }
            }
        )
        print(f"Index '{ELASTICSEARCH_INDEX}' créé avec succès.")

    # Extraction des documents depuis MongoDB
    documents = list(collection.find({}))
    print(f"{len(documents)} documents extraits depuis MongoDB.")

    # Préparation des documents pour Elasticsearch
    actions = []
    for doc in documents:
        # Conversion de l'ID MongoDB en chaîne
        doc_id = str(doc.pop("_id"))

        # Transformation de la date au format yyyy-MM-dd si nécessaire
        if "competition_date" in doc and doc["competition_date"]:
            try:
                doc["competition_date"] = convert_date_to_iso(doc["competition_date"])
            except ValueError:
                print(f"Erreur dans le format de la date pour le document ID {doc_id}: {doc['competition_date']}")
                continue

        # Préparation de l'action pour Elasticsearch
        actions.append({
            "_index": ELASTICSEARCH_INDEX,
            "_id": doc_id,
            "_source": doc
        })

    # Insertion des documents dans Elasticsearch
    try:
        helpers.bulk(es, actions)
        print(f"Synchronisation réussie : {len(actions)} documents insérés dans Elasticsearch.")
    except helpers.BulkIndexError as e:
        print(f"Erreur lors de l'insertion en masse dans Elasticsearch : {e.errors}")
        raise

def convert_date_to_iso(date_str):
    """
    Convertit une date en chaîne en format yyyy-MM-dd.
    :param date_str: Date en chaîne (exemple : "01/03/2020").
    :return: Date au format ISO (yyyy-MM-dd).
    """
    from datetime import datetime

    try:
        # Si le format est déjà yyyy-MM-dd, retourne directement
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass

    try:
        # Si le format est dd/MM/yyyy, convertit en yyyy-MM-dd
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Format de date non valide : {date_str}")

if __name__ == "__main__":
    Mongo_Elastic()
