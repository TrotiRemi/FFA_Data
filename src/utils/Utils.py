import os
from elasticsearch import Elasticsearch
import pandas as pd
import json
import plotly.express as px
from pymongo import MongoClient

# Connexion Elasticsearch
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "athle_results")
es = Elasticsearch(hosts=[ELASTICSEARCH_URL])

# Charger le GeoJSON des départements français
def load_geojson():
    geojson_path = os.path.join('data', 'departements.geojson')
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data

                                            #Map

# Récupérer les données d'Elasticsearch
def get_department_data():
    geojson_data = load_geojson()
    all_departments = [feature["properties"]["code"].lstrip("0") for feature in geojson_data["features"]]
    query = {
        "size": 0,
        "aggs": {
            "departments_count": {
                "terms": {
                    "field": "department.keyword",
                    "size": 100
                }
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    buckets = response["aggregations"]["departments_count"]["buckets"]
    department_data = {bucket["key"].lstrip("0"): bucket["doc_count"] for bucket in buckets}
    complete_data = {dep: department_data.get(dep, 0) for dep in all_departments}

    return complete_data


def generate_map():
    geojson_data = load_geojson()
    department_data = get_department_data()
    df = pd.DataFrame([
        {"department": k, "count": v} for k, v in department_data.items()
    ])
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations="department",
        color="count",
        featureidkey="properties.code", 
        color_continuous_scale="Viridis",
        range_color=(0, df["count"].max()),
        mapbox_style="carto-positron",
        zoom=4.3,
        center={"lat": 46.603354, "lon": 1.888334},
        title="Carte des Départements Français"
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

# Récupérer les données d'Elasticsearch pour le nombre de compétitions par département
def get_competition_data():
    geojson_data = load_geojson()
    all_departments = [feature["properties"]["code"].lstrip("0") for feature in geojson_data["features"]]
    query = {
        "size": 0,
        "aggs": {
            "departments": {
                "terms": {
                    "field": "department.keyword",
                    "size": 100
                },
                "aggs": {
                    "competitions": {
                        "cardinality": {
                            "script": {
                                "source": """
                                    if (doc['competition_date'].size() > 0 && doc['competition_name.keyword'].size() > 0) {
                                        return doc['competition_name.keyword'].value + ' ' + doc['competition_date'].value.getYear();
                                    } else {
                                        return null;
                                    }
                                """,
                                "lang": "painless"
                            }
                        }
                    }
                }
            }
        }
    }

    try:
        response = es.search(index=ELASTICSEARCH_INDEX, body=query)
        buckets = response["aggregations"]["departments"]["buckets"]
        department_data = {bucket["key"].lstrip("0"): bucket["competitions"]["value"] for bucket in buckets}
        for dom_code in ["971", "972", "973", "974", "976"]:
            if dom_code not in department_data:
                department_data[dom_code] = 0
        complete_data = {dep: department_data.get(dep, 0) for dep in all_departments}
        return complete_data

    except Exception as e:
        print(f"Erreur lors de la récupération des données Elasticsearch : {e}")
        return {dep: 0 for dep in all_departments}



def generate_competition_map():
    geojson_data = load_geojson()
    department_data = get_competition_data()
    all_departments = [feature["properties"]["code"].lstrip("0") for feature in geojson_data["features"]]
    complete_data = {dep: department_data.get(dep, 0) for dep in all_departments}
    df = pd.DataFrame([
        {"department": k, "count": v} for k, v in complete_data.items()
    ])
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations="department",
        color="count",
        featureidkey="properties.code", 
        color_continuous_scale="Viridis",
        range_color=(0, df["count"].max()), 
        mapbox_style="carto-positron",
        zoom=4.3,
        center={"lat": 46.603354, "lon": 1.888334},
        title="Carte des Compétitions par Département"
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

                                                 #Fonction pour le code Coureur.py

def get_data_from_mongo(filters=None):
    """
    Récupère les données de MongoDB en fonction des filtres donnés.
    :param filters: Dictionnaire des filtres pour la recherche.
    :return: DataFrame Pandas contenant les données.
    """
    MONGO_URI = "mongodb://mongodb:27017/"
    MONGO_DATABASE = "athle_database"
    MONGO_COLLECTION = "results"
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[MONGO_COLLECTION]

    query = filters if filters else {}
    data = list(collection.find(query))

    if data:
        df = pd.DataFrame(data)
        return df
    return pd.DataFrame()


def search_in_elasticsearch(name, club, distance_min, distance_max, day, month, year, size=100):
    query = {
        "bool": {
            "must": [],
            "filter": []
        }
    }
    
    if name:
        query["bool"]["must"].append({"match_phrase": {"athlete": name}})
    if club:
        query["bool"]["must"].append({"match_phrase": {"club": club}})
    if distance_min or distance_max:
        range_query = {}
        if distance_min:
            range_query["gte"] = distance_min
        if distance_max:
            range_query["lte"] = distance_max
        query["bool"]["filter"].append({"range": {"distance": range_query}})
    if day or month or year:
        date_query = ""
        if day:
            date_query += f"{int(day):02}/"
        if month:
            date_query += f"{int(month):02}/"
        if year:
            date_query += f"{int(year):02}"
        query["bool"]["must"].append({"wildcard": {"competition_date": f"*{date_query}*"}})

    es = Elasticsearch(hosts=["http://elasticsearch:9200"])
    try:
        response = es.search(index=ELASTICSEARCH_INDEX, query=query, size=size)
        hits = response["hits"]["hits"]
        results = [hit["_source"] for hit in hits]
        return results

    except Exception as e:
        print(f"Erreur lors de la recherche Elasticsearch : {e}")
        return []

    except Exception as e:
        print(f"Erreur lors de la recherche Elasticsearch : {e}")
        return []

# Fonction pour formater le temps en H:M:S à partir de Minute_Time
def format_time_from_minutes(minutes):
    try:
        total_seconds = int(float(minutes) * 60)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"
    except:
        return "00:00" 
    

def update_search_result(n_clicks, name, club, distance_min, distance_max, day, month, year):
    if n_clicks > 0:
        filtered_data = search_in_elasticsearch(name, club, distance_min, distance_max, day, month, year)
        if isinstance(filtered_data, list) and filtered_data: 
            filtered_data = pd.DataFrame(filtered_data)
        elif isinstance(filtered_data, list): 
            return "Aucun résultat trouvé.", []
        if not filtered_data.empty:
            if 'Minute_Time' in filtered_data.columns:
                filtered_data['time'] = filtered_data['Minute_Time'].fillna(0).astype(float)
            else:
                return "La colonne 'Minute_Time' est absente des résultats.", []
            table_data = filtered_data.to_dict('records')
            result_text = f"{len(filtered_data)} résultat(s) trouvé(s)."
        else:
            table_data = []
            result_text = "Aucun résultat trouvé."
        
        return result_text, table_data

    return "", []


                                                   #Histogramme

# Fonction pour récupérer toutes les compétitions avec leurs années
def get_competitions():
    query = {
        "size": 0,
        "aggs": {
            "competitions": {
                "terms": {
                    "field": "competition_name.keyword", 
                    "size": 1000
                },
                "aggs": {
                    "years": {
                        "terms": {
                            "script": "doc['competition_date'].value.year", 
                            "size": 1000
                        }
                    }
                }
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    competitions = []
    for bucket in response["aggregations"]["competitions"]["buckets"]:
        for year_bucket in bucket["years"]["buckets"]:
            competition_with_year = f"{bucket['key']} {year_bucket['key']}" 
            competitions.append(competition_with_year)
    return competitions


# Fonction pour récupérer les distances d'une compétition
def get_distances(competition_name, year):
    query = {
        "size": 100,
        "_source": ["distance"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"competition_name.keyword": competition_name}},
                    {"range": {"competition_date": {"gte": f"{year}-01-01", "lte": f"{year}-12-31"}}}
                ]
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    distances = {doc["_source"]["distance"] for doc in response["hits"]["hits"]}
    return sorted(distances)

# Fonction pour récupérer les données filtrées
def get_filtered_data(competition_name, year, distance):
    query = {
        "size": 10000,
        "_source": ["Minute_Time"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"competition_name.keyword": competition_name}},
                    {"range": {"competition_date": {"gte": f"{year}-01-01", "lte": f"{year}-12-31"}}},
                    {"term": {"distance": distance}}
                ]
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    data = [doc["_source"] for doc in response["hits"]["hits"]]
    return pd.DataFrame(data)