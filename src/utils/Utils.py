import os
from elasticsearch import Elasticsearch
import pandas as pd
import json
import plotly.express as px

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

# Récupérer les données d'Elasticsearch
def get_department_data():
    # Charger les départements depuis le GeoJSON
    geojson_data = load_geojson()
    all_departments = [feature["properties"]["code"].lstrip("0") for feature in geojson_data["features"]]

    # Requête Elasticsearch
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

    # Normaliser les résultats Elasticsearch et inclure tous les départements avec 0
    department_data = {bucket["key"].lstrip("0"): bucket["doc_count"] for bucket in buckets}
    complete_data = {dep: department_data.get(dep, 0) for dep in all_departments}

    return complete_data


def generate_map():
    # Charger le GeoJSON
    geojson_data = load_geojson()

    # Récupérer les données Elasticsearch
    department_data = get_department_data()

    # Transformer les données en DataFrame
    df = pd.DataFrame([
        {"department": k, "count": v} for k, v in department_data.items()
    ])

    # Créer la carte
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations="department",
        color="count",
        featureidkey="properties.code",  # Liaison entre GeoJSON et DataFrame
        color_continuous_scale="Viridis",
        range_color=(0, df["count"].max()),
        mapbox_style="carto-positron",
        zoom=4.3,
        center={"lat": 46.603354, "lon": 1.888334},  # France
        title="Carte des Départements Français"
    )

    # Mise en forme
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
