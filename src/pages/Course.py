import dash
from dash import html, dcc, Input, Output, State, dash_table
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer
import pandas as pd
from datetime import datetime


# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/Course')

# Configuration Elasticsearch
ELASTICSEARCH_URL = "http://elasticsearch:9200"
ELASTICSEARCH_INDEX = "athle_results"
es = Elasticsearch(hosts=[ELASTICSEARCH_URL])

# Liste des champs de recherche
search_fields = [
    {'id': 'search-name', 'placeholder': 'Nom de la Course', 'column': 'competition_name', 'type': 'text'},
    {'id': 'search-level', 'placeholder': 'Niveau', 'column': 'level', 'type': 'text'},
    {'id': 'search-date', 'placeholder': 'Date (J/M/A)', 'column': 'competition_date', 'type': 'text'},
    {'id': 'search-type', 'placeholder': 'Type de compétition', 'column': 'type', 'type': 'text'},
    {'id': 'search-dep', 'placeholder': 'Département', 'column': 'department', 'type': 'text'}
]

# Layout
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Chercher une course", style={'textAlign': 'center'}),

    # Champs de recherche
    html.Div([
        html.Div([
            dcc.Input(
                id=field['id'] + '-page2',
                type=field['type'],
                placeholder=field['placeholder'],
                style={'width': '70%', 'padding': '10px', 'margin-bottom': '10px'}
            )
            for field in search_fields
        ], style={'textAlign': 'center', 'margin-top': '20px'}),

        html.Button(
            'Rechercher',
            id='search-button-page2',
            n_clicks=0,
            style={'padding': '10px 20px', 'background-color': '#007BFF', 'color': '#fff', 'border': 'none'}
        ),
        html.Div(id='search-result-page2', style={'margin-top': '20px', 'font-size': '16px', 'color': '#333'})
    ], style={'textAlign': 'center'}),

    # Tableau des résultats
    html.Div(
        dash_table.DataTable(
            id='result-table-page2',
            columns=[
                {"name": "Date", "id": "competition_date"},
                {"name": "Nom", "id": "competition_name"},
                {"name": "Distance", "id": "distance"},
                {"name": "Nombre de Coureurs (Total)", "id": "total_runners"},
                {"name": "Nombre de Coureurs (Distance)", "id": "distance_runners"}
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
    [Output('search-result-page2', 'children'),
     Output('result-table-page2', 'data')],
    [Input('search-button-page2', 'n_clicks')],
    [State(field['id'] + '-page2', 'value') for field in search_fields]
)
def update_page2(n_clicks, *args):
    if n_clicks > 0:
        filters = [{"match_phrase": {field['column']: value}} for field, value in zip(search_fields, args) if value]
        query = {
            "bool": {
                "must": filters
            }
        }

        try:
            response = es.search(
                index=ELASTICSEARCH_INDEX,
                body={
                    "size": 0,
                    "query": query,
                    "aggs": {
                        "competitions": {
                            "composite": {
                                "sources": [
                                    {"competition_name": {"terms": {"field": "competition_name.keyword"}}},
                                    {"competition_date": {"terms": {"field": "competition_date"}}}
                                ],
                                "size": 10000
                            },
                            "aggregations": {
                                "distances": {
                                    "terms": {"field": "distance"},
                                    "aggs": {
                                        "runner_count": {
                                            "value_count": {"field": "distance"}
                                        }
                                    }
                                },
                                "total_runners": {
                                    "sum_bucket": {
                                        "buckets_path": "distances>_count"
                                    }
                                }
                            }
                        }
                    }
                }
            )

            data = []
            for bucket in response['aggregations']['competitions']['buckets']:
                competition_name = bucket['key']['competition_name']
                raw_date = bucket['key']['competition_date']
                competition_date = datetime.utcfromtimestamp(raw_date / 1000).strftime('%Y-%m-%d')

                total_runners = bucket['total_runners']['value']

                for distance_bucket in bucket['distances']['buckets']:
                    distance = distance_bucket['key']
                    runners_on_distance = distance_bucket['doc_count']

                    data.append({
                        "competition_date": competition_date, 
                        "competition_name": competition_name,
                        "type": "N/A" if "type" not in bucket else bucket["type"],
                        "distance": distance,
                        "total_runners": total_runners,
                        "distance_runners": runners_on_distance
                    })
            result_text = f"{len(data)} résultat(s) trouvé(s)." if data else "Aucun résultat trouvé."
            return result_text, data

        except Exception as e:
            print(f"Erreur Elasticsearch : {e}")
            return "Erreur lors de la récupération des données.", []

    return "", []