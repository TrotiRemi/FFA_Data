import dash
from dash import html, dcc, Input, Output, State, dash_table
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer
import pandas as pd
from pymongo import MongoClient

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/')

# Configuration ElasticSearch
ELASTICSEARCH_URL = "http://elasticsearch:9200"
ELASTICSEARCH_INDEX = "athle_results"

MONGO_URI = "mongodb://mongodb:27017/"
MONGO_DATABASE = "athle_database"
MONGO_COLLECTION = "results"


def get_data_from_mongo(filters=None):
    """
    Récupère les données de MongoDB en fonction des filtres donnés.
    :param filters: Dictionnaire des filtres pour la recherche.
    :return: DataFrame Pandas contenant les données.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[MONGO_COLLECTION]

    query = filters if filters else {}
    data = list(collection.find(query))

    # Convertir en DataFrame Pandas
    if data:
        df = pd.DataFrame(data)
        return df
    return pd.DataFrame()  # DataFrame vide si aucune donnée trouvée
def search_in_elasticsearch(name, club, distance_min, distance_max, day, month, year):
    query = {
        "bool": {
            "must": [],
            "filter": []
        }
    }

    # Ajout des filtres selon les champs
    if name:
        query["bool"]["must"].append({"match": {"athlete": name}})
    if club:
        query["bool"]["must"].append({"match": {"club": club}})
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

    # Recherche dans Elasticsearch
    es = Elasticsearch(hosts=["http://elasticsearch:9200"])
    ELASTICSEARCH_INDEX = "athle_results"
    
    try:
        response = es.search(index=ELASTICSEARCH_INDEX, query=query)
        hits = response["hits"]["hits"]
        results = [hit["_source"] for hit in hits]  # Extraire les données sources
        return results
    except Exception as e:
        print(f"Erreur lors de la recherche Elasticsearch : {e}")
        return []



# Liste des champs de recherche
search_fields = [
    {'id': 'search-name', 'placeholder': 'Nom', 'column': 'athlete', 'type': 'text'},
    {'id': 'search-club', 'placeholder': 'Club', 'column': 'club', 'type': 'text'},
    {'id': 'search-distance-min', 'placeholder': 'Distance minimale', 'column': 'distance_min', 'type': 'number'},
    {'id': 'search-distance-max', 'placeholder': 'Distance maximale', 'column': 'distance_max', 'type': 'number'}
]

# Fonction pour formater le temps en H:M:S à partir de Minute_Time
def format_time_from_minutes(minutes):
    try:
        total_seconds = int(float(minutes) * 60)  # Convertir les minutes en secondes
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Retourner H:M:S si heures > 0, sinon M:S
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"
    except:
        return "00:00"  # Valeur par défaut en cas d'erreur

# Layout principal de la page
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Chercher un coureur", style={'textAlign': 'center'}),

    # Barres de recherche
    html.Div([
        html.Div([
            dcc.Input(
                id=field['id'],
                type=field['type'],
                placeholder=field['placeholder'],
                style={'width': '70%', 'padding': '10px', 'margin-bottom': '10px'}
            )
            for field in search_fields if field['column'] not in ['distance_min', 'distance_max', 'date']
        ], style={'textAlign': 'center', 'margin-top': '20px'}),

        html.Div([
            html.Label("Distance :", style={
                'font-weight': 'bold',
                'margin-right': '10px',
                'align-self': 'center'
            }),
            dcc.Input(
                id='search-distance-min',
                type='number',
                placeholder='Min',
                style={'width': '80px', 'padding': '5px', 'margin-right': '10px', 'display': 'inline-block'}
            ),
            dcc.Input(
                id='search-distance-max',
                type='number',
                placeholder='Max',
                style={'width': '80px', 'padding': '5px', 'margin-right': '10px', 'display': 'inline-block'}
            )
        ], style={
            'display': 'flex',
            'align-items': 'center',
            'margin-top': '5px',
            'margin-left': '9%'
        }),

        html.Div([
            html.Div([
                html.Label("Date :", style={
                    'font-weight': 'bold',
                    'margin-right': '10px',
                    'align-self': 'center'
                }),
                dcc.Dropdown(
                    id='search-day',
                    options=[{'label': f"{day:02}", 'value': f"{day:02}"} for day in range(1, 32)],
                    placeholder='Jour',
                    style={'width': '80px', 'display': 'inline-block', 'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='search-month',
                    options=[{'label': f"{month:02}", 'value': f"{month:02}"} for month in range(1, 13)],
                    placeholder='Mois',
                    style={'width': '80px', 'display': 'inline-block', 'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='search-year',
                    options=[{'label': f"{year % 100:02}", 'value': f"{year % 100:02}"} for year in range(2000, 2031)],
                    placeholder='Année',
                    style={'width': '80px', 'display': 'inline-block'}
                )
            ], style={
                'display': 'flex',
                'align-items': 'center',
                'margin-top': '5px',
                'margin-left': '10.75%'
            })
        ]),

        html.Button(
            'Rechercher',
            id='search-button',
            n_clicks=0,
            style={'padding': '10px 20px', 'background-color': '#007BFF', 'color': '#fff', 'border': 'none', 'margin-top': '20px'}
        ),
        html.Div(id='search-result', style={'margin-top': '20px', 'font-size': '16px', 'color': '#333'})
    ], style={'textAlign': 'center'}),

    # Tableau des résultats
    html.Div(
        dash_table.DataTable(
            id='result-table',
            columns=[
                {"name": "Classement", "id": "rank"},
                {"name": "Athlete", "id": "athlete"},
                {"name": "Club", "id": "club"},
                {"name": "Date", "id": "competition_date"},
                {"name": "Course", "id": "competition_name"},
                {"name": "Temps", "id": "formatted_time"},
                {"name": "Vitesse", "id": "vitesse"},
                {"name": "Distance", "id": "distance"}
            ],
            data=[],  # Données initialement vides
            style_table={'margin-top': '20px', 'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': '150px',
                'minWidth': '100px',
            },
            style_data={'height': 'auto'},
            style_header={'fontWeight': 'bold'}
        ),
        style={'width': '80%', 'margin': '0 auto'}
    ),

    Footer()
])

# Callback pour mettre à jour les résultats de recherche et le tableau
@dash.callback(
    [Output('search-result', 'children'),
     Output('result-table', 'data')],
    [Input('search-button', 'n_clicks')],
    [State('search-name', 'value'),
     State('search-club', 'value'),
     State('search-distance-min', 'value'),
     State('search-distance-max', 'value'),
     State('search-day', 'value'),
     State('search-month', 'value'),
     State('search-year', 'value')]
)
def update_search_result(n_clicks, name, club, distance_min, distance_max, day, month, year):
    if n_clicks > 0:
        # Appeler la fonction de recherche
        filtered_data = search_in_elasticsearch(name, club, distance_min, distance_max, day, month, year)
        
        # Vérifier si `filtered_data` est vide après conversion
        if isinstance(filtered_data, list) and filtered_data:  # Si c'est une liste non vide
            filtered_data = pd.DataFrame(filtered_data)
        elif isinstance(filtered_data, list):  # Si c'est une liste vide
            return "Aucun résultat trouvé.", []
        
        # Si les données existent, préparer la table pour Dash
        if not filtered_data.empty:
            # Remplacer la colonne `time` par `Minute_Time` (au format float)
            filtered_data['time'] = filtered_data['Minute_Time'].astype(float)

            # Convertir les données en dictionnaire pour Dash
            table_data = filtered_data.to_dict('records')
            result_text = f"{len(filtered_data)} résultat(s) trouvé(s)."
        else:
            table_data = []
            result_text = "Aucun résultat trouvé."
        
        return result_text, table_data

    return "", []

