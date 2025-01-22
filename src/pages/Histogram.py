import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer

# Connexion à Elasticsearch
ELASTICSEARCH_URL = "http://elasticsearch:9200"
ELASTICSEARCH_INDEX = "athle_results"
es = Elasticsearch(hosts=[ELASTICSEARCH_URL])

# Enregistrement de la page
dash.register_page(__name__, path='/Histogram')

# Fonction pour récupérer toutes les compétitions
def get_competitions():
    query = {
        "size": 0,
        "aggs": {
            "competition_names": {
                "terms": {
                    "field": "competition_name.keyword",  # Utilisation du sous-champ keyword
                    "size": 1000
                }
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    print("Réponse Elasticsearch pour get_competitions :", response)  # Debugging
    competitions = [bucket["key"] for bucket in response["aggregations"]["competition_names"]["buckets"]]
    print("Compétitions récupérées :", competitions)  # Debugging
    return competitions



# Fonction pour récupérer les distances d'une compétition
def get_distances(competition_name):
    query = {
        "size": 100,
        "_source": ["distance"],
        "query": {
            "term": {
                "competition_name.keyword": competition_name
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    distances = {doc["_source"]["distance"] for doc in response["hits"]["hits"]}
    print(f"Distances pour la compétition {competition_name} :", distances)  # Debugging
    return sorted(distances)

# Fonction pour récupérer les données filtrées
def get_filtered_data(competition_name, distance):
    query = {
        "size": 10000,  # Ajustez selon le volume de données attendu
        "_source": ["Minute_Time"],
        "query": {
            "bool": {
                "must": [
                    {"term": {"competition_name.keyword": competition_name}},
                    {"term": {"distance": distance}}
                ]
            }
        }
    }
    response = es.search(index=ELASTICSEARCH_INDEX, body=query)
    data = [doc["_source"] for doc in response["hits"]["hits"]]
    print(f"Données récupérées pour {competition_name} (distance {distance}m): {len(data)} entrées")  # Debugging
    return pd.DataFrame(data)

# Layout de la page
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Analyse des Compétitions"),
    
    # Menu déroulant pour sélectionner une compétition
    html.Label("Choisissez une compétition"),
    dcc.Dropdown(
        id="competition-dropdown",
        options=[],  # Options vides initialement
        placeholder="Sélectionnez une compétition"
    ),

    # Menu déroulant pour sélectionner une distance
    html.Label("Choisissez une distance"),
    dcc.Dropdown(
        id="distance-dropdown",
        options=[],  # Options vides initialement
        placeholder="Sélectionnez une distance",
        disabled=True  # Désactivé tant qu'une compétition n'est pas sélectionnée
    ),

    # Graphique d'histogramme
    dcc.Graph(id="histogram"),
    Footer()
])

# Callbacks
@callback(
    Output("competition-dropdown", "options"),
    Input("competition-dropdown", "id")
)
def load_competitions(_):
    # Charger dynamiquement les compétitions
    competitions = get_competitions()
    if not competitions:
        print("Aucune compétition trouvée")  # Debugging
    return [{"label": name, "value": name} for name in competitions]

@callback(
    Output("distance-dropdown", "options"),
    Output("distance-dropdown", "disabled"),
    Input("competition-dropdown", "value")
)
def update_distances(competition_name):
    if competition_name:
        distances = get_distances(competition_name)
        if not distances:
            print(f"Aucune distance trouvée pour la compétition {competition_name}")  # Debugging
        options = [{"label": str(d), "value": d} for d in distances]
        return options, False
    return [], True

@callback(
    Output("histogram", "figure"),
    Input("competition-dropdown", "value"),
    Input("distance-dropdown", "value")
)
def update_histogram(competition_name, distance):
    if competition_name and distance:
        data = get_filtered_data(competition_name, distance)
        if not data.empty:
            fig = px.histogram(
                data,
                x="Minute_Time",
                nbins=20,  # Nombre de barres dans l'histogramme
                title=f"Distribution des temps pour {competition_name} ({distance}m)",
                labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"}
            )
            fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
            return fig
    
    # Générer un histogramme vide par défaut
    empty_data = pd.DataFrame({"Minute_Time": []})
    fig = px.histogram(
        empty_data,
        x="Minute_Time",
        nbins=1,  # Aucun bin
        title="Aucune donnée disponible",
        labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"}
    )
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    return fig
