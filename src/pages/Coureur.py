import dash
from dash import html, dcc, Input, Output, State, dash_table
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer
import pandas as pd
from pymongo import MongoClient
from src.utils.Utils import search_in_elasticsearch

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/')

# Configuration Elasticsearch
ELASTICSEARCH_URL = "http://elasticsearch:9200"
ELASTICSEARCH_INDEX = "athle_results"
es = Elasticsearch(hosts=[ELASTICSEARCH_URL])


# Liste des champs de recherche
search_fields = [
    {'id': 'search-first-name', 'placeholder': 'Prénom', 'column': 'first_name', 'type': 'text'},
    {'id': 'search-last-name', 'placeholder': 'Nom', 'column': 'last_name', 'type': 'text'},
    {'id': 'search-club', 'placeholder': 'Club', 'column': 'club', 'type': 'text'},
    {'id': 'search-distance-min', 'placeholder': 'Distance minimale', 'column': 'distance_min', 'type': 'number'},
    {'id': 'search-distance-max', 'placeholder': 'Distance maximale', 'column': 'distance_max', 'type': 'number'}
]

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
            for field in search_fields if field['column'] not in ['distance_min', 'distance_max', 'date', 'club']
        ], style={'textAlign': 'center', 'margin-top': '20px'}),
        
        html.Div([
            dcc.Dropdown(
                id='search-club',
                options=[],  # Options chargées dynamiquement
                placeholder="Sélectionnez un club",
                searchable=True,
                style={
                    'width': '80%',  # Ajuste la largeur à 80% de la div parent
                    'margin': '0 auto',  # Centre horizontalement l'élément
                    'height': '45px',  # Ajuste la hauteur pour plus de lisibilité
                    'margin-left': '7.7%',
                    'font-size': '16px',  # Agrandir le texte pour améliorer l'affichage
                    'textAlign': 'left',  # Aligne le texte à gauche
                }
            )
        ], style={'textAlign': 'center', 'margin-bottom': '10px'}),


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
                    style={'width': '100px', 'display': 'inline-block', 'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='search-month',
                    options=[{'label': f"{month:02}", 'value': f"{month:02}"} for month in range(1, 13)],
                    placeholder='Mois',
                    style={'width': '100px', 'display': 'inline-block', 'margin-right': '10px'}
                ),
                dcc.Dropdown(
                    id='search-year',
                    options=[{'label': str(year), 'value': str(year)} for year in range(2000, 2031)],
                    placeholder='Année',
                    style={'width': '100px', 'display': 'inline-block'}
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
                {"name": "Temps", "id": "time"},
                {"name": "Vitesse", "id": "vitesse"},
                {"name": "Distance", "id": "distance"}
            ],
            data=[],
            fixed_rows={'headers': True},

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
    [State('search-first-name', 'value'),
     State('search-last-name', 'value'),
     State('search-club', 'value'),
     State('search-distance-min', 'value'),
     State('search-distance-max', 'value'),
     State('search-day', 'value'),
     State('search-month', 'value'),
     State('search-year', 'value')]
)
def update_search_result(n_clicks, first_name, last_name, club, distance_min, distance_max, day, month, year):
    if n_clicks > 0:
        filtered_data = search_in_elasticsearch(first_name, last_name, club, distance_min, distance_max, day, month, year)

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

@dash.callback(
    Output('search-club', 'options'),
    Input('search-club', 'id')  # Se déclenche à l'initialisation
)
def load_clubs(_):
    try:
        response = es.search(
            index=ELASTICSEARCH_INDEX,
            body={
                "size": 10000,  # Récupère jusqu'à 10 000 documents
                "_source": ["club"]  # Ne récupère que le champ "club"
            }
        )

        # Extraire les valeurs uniques des clubs
        clubs = list(set(hit["_source"]["club"] for hit in response["hits"]["hits"] if "club" in hit["_source"]))

        return [{"label": club, "value": club} for club in clubs]

    except Exception as e:
        print(f"Erreur Elasticsearch lors du chargement des clubs : {e}")
        return []
