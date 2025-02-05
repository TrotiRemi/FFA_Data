import dash
from dash import html, dcc, Input, Output, State, dash_table
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer
import pandas as pd
from datetime import datetime

# Enregistrement de la page
dash.register_page(__name__, path='/Course')

# Configuration Elasticsearch
ELASTICSEARCH_URL = "http://elasticsearch:9200"
ELASTICSEARCH_INDEX = "athle_results"
es = Elasticsearch(hosts=[ELASTICSEARCH_URL])

# Mapping des niveaux
LEVEL_MAPPING = {
    "Dép": "Départemental",
    "Rég": "Régional",
    "Int": "Interrégional",
    "Nat": "National"
}

# Style général appliqué à tous les éléments pour une police moderne
general_style = {
    'fontFamily': "'Poppins', sans-serif"
}

# Style spécifique pour le titre
# 🎨 Nouveau style du titre (même que pour l'histogramme)
title_style = {
    'textAlign': 'center',
    'fontFamily': "'Poppins', sans-serif",
    'fontWeight': 'bold',
    'fontSize': '32px',
    'color': '#0d2366',
    'textShadow': '2px 2px 4px rgba(0, 0, 0, 0.3)',
    'marginBottom': '30px',
    'display': 'inline-block',
    'marginRight': '10px',
    'verticalAlign': 'middle'
}



# Style pour aligner les labels et dropdowns
common_style = {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'flex-start',
    'width': '50%',
    'margin-left': '4%',
    'margin-bottom': '15px',
    'height': '40px',
    'fontFamily': "'Poppins', sans-serif"
}
# Style spécifique pour le titre
title_style = {
    'textAlign': 'center',
    'fontFamily': "'Poppins', sans-serif",
    'fontSize': '32px',
    'fontWeight': 'bold',
    'background': 'linear-gradient(to right, #0d2366, #007BFF)',
    'WebkitBackgroundClip': 'text',
    'WebkitTextFillColor': 'transparent',
    'textShadow': '1px 1px 2px rgba(0, 0, 0, 0.2)',
    'letterSpacing': '1px',
    'marginTop': '20px'
}

# Layout de la page
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Chercher une course", style=title_style),


    # Champs de recherche
    html.Div([
        # Section Date centrée et avec une police moderne
        html.Div([
            html.Label("Date :", style={'fontWeight': 'bold', 'margin-right': '10px', 'alignSelf': 'center', **general_style}),
            dcc.Dropdown(
                id='search-day-course',
                options=[{'label': f"{day:02}", 'value': f"{day:02}"} for day in range(1, 32)],
                placeholder='Jour',
                style={'width': '100px', 'display': 'inline-block', 'margin-right': '10px', **general_style}
            ),
            dcc.Dropdown(
                id='search-month-course',
                options=[{'label': f"{month:02}", 'value': f"{month:02}"} for month in range(1, 13)],
                placeholder='Mois',
                style={'width': '100px', 'display': 'inline-block', 'margin-right': '10px', **general_style}
            ),
            dcc.Dropdown(
                id='search-year-course',
                options=[{'label': str(year), 'value': str(year)} for year in range(2000, 2031)],
                placeholder='Année',
                style={'width': '100px', 'display': 'inline-block', **general_style}
            )
        ], style={'display': 'flex', 'align-items': 'center', 'margin-top': '5px', 'margin-left': '10.75%', 'margin-bottom': '15px'}),

        # Dropdown pour Nom de la Course
        html.Div([
            html.Label("Nom de la Course :", style={'fontWeight': 'bold', 'width': '20%', **general_style}),
            dcc.Dropdown(
                id='search-competition-page2',
                options=[],
                placeholder="Sélectionnez une course",
                searchable=True,
                style={'width': '78%', 'height': '45px', 'font-size': '16px', **general_style}
            )
        ], style=common_style),

        # Dropdown pour Niveau
        html.Div([
            html.Label("Niveau de la Course :", style={'fontWeight': 'bold', 'width': '20%', **general_style}),
            dcc.Dropdown(
                id='search-level-page2',
                options=[],
                placeholder="Sélectionnez un Niveau",
                searchable=True,
                style={'width': '78%', 'height': '45px', 'font-size': '16px', **general_style}
            )
        ], style=common_style),

        # Dropdown pour Département
        html.Div([
            html.Label("Département de la Course :", style={'fontWeight': 'bold', 'width': '20%', **general_style}),
            dcc.Dropdown(
                id='search-department-page2',
                options=[],
                placeholder="Sélectionnez un Département",
                searchable=True,
                style={'width': '78%', 'height': '45px', 'font-size': '16px', **general_style}
            )
        ], style=common_style),

        html.Button(
            'Rechercher',
            id='search-button-page2',
            n_clicks=0,
            style={'padding': '10px 20px', 'backgroundColor': '#007BFF', 'color': '#fff', 'border': 'none', **general_style}
        ),
        html.Div(id='search-result-page2', style={'margin-top': '20px', 'font-size': '16px', 'color': '#333', **general_style})
    ], style={'textAlign': 'center'}),

    # Tableau des résultats
    html.Div(
        dash_table.DataTable(
            id='result-table-page2',
            columns=[
                {"name": "Date", "id": "competition_date"},
                {"name": "Nom", "id": "competition_name"},
                {"name": "Niveau", "id": "level"},
                {"name": "Département", "id": "department"},
                {"name": "Distance", "id": "distance"},
                {"name": "Type", "id": "type_course"},
                {"name": "Ligue", "id": "ligue"},
                {"name": "Nombre de Coureurs (Total)", "id": "total_runners"},
                {"name": "Nombre de Coureurs (Distance)", "id": "distance_runners"}
            ],
            data=[],
            fixed_rows={'headers': True},
            style_table={'margin-top': '20px', 'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': "'Poppins', sans-serif"},
            style_header={'fontWeight': 'bold', **general_style}
        ),
        style={'width': '80%', 'margin': '0 auto'}
    ),
    
    Footer()
])


# Callback pour récupérer tous les niveaux disponibles dans Elasticsearch
@dash.callback(
    Output('search-level-page2', 'options'),
    Input('search-level-page2', 'id')
)
def load_levels(_):
    try:
        response = es.search(
            index=ELASTICSEARCH_INDEX,
            body={
                "size": 0,
                "aggs": {
                    "unique_levels": {
                        "terms": {"field": "level.keyword", "size": 1000}
                    }
                }
            }
        )

        levels = [bucket['key'] for bucket in response["aggregations"]["unique_levels"]["buckets"]]
        
        # Transformer les abréviations en noms complets
        return [{"label": LEVEL_MAPPING.get(level, level), "value": level} for level in levels]
    
    except Exception as e:
        print(f"Erreur Elasticsearch lors du chargement des niveaux : {e}")
        return []


@dash.callback(
    [Output('search-result-page2', 'children'),
     Output('result-table-page2', 'data')],
    [Input('search-button-page2', 'n_clicks')],
    [State('search-competition-page2', 'value'),
     State('search-department-page2', 'value'),
     State('search-level-page2', 'value'),
     State('search-day-course', 'value'),
     State('search-month-course', 'value'),
     State('search-year-course', 'value')]
)
def update_page2(n_clicks, search_competition, search_department, search_level, search_day, search_month, search_year):
    if n_clicks > 0:
        # Création du filtre basé sur les valeurs remplies par l'utilisateur
        filters = []
        if search_competition:
            filters.append({"match_phrase": {"competition_name.keyword": search_competition}})
        if search_department:
            filters.append({"match_phrase": {"department.keyword": search_department}})
        if search_level:
            filters.append({"match_phrase": {"level.keyword": search_level}})

        # Gestion du filtre date
        if search_year:
            date_range = {"gte": f"{search_year}-01-01", "lte": f"{search_year}-12-31"}
            if search_month:
                date_range["gte"] = f"{search_year}-{search_month}-01"
                date_range["lte"] = f"{search_year}-{search_month}-31"
            if search_day:
                date_range["gte"] = f"{search_year}-{search_month}-{search_day}"
                date_range["lte"] = f"{search_year}-{search_month}-{search_day}"

            filters.append({"range": {"competition_date": date_range}})

        query = {"bool": {"must": filters}}

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
                                    {"competition_date": {"terms": {"field": "competition_date"}}},
                                    {"level": {"terms": {"field": "level.keyword"}}},
                                    {"department": {"terms": {"field": "department.keyword"}}},
                                    {"type_course": {"terms": {"field": "type_course.keyword"}}},
                                    {"ligue": {"terms": {"field": "ligue.keyword"}}}
                                ],
                                "size": 10000
                            },
                            "aggregations": {
                                "distances": {
                                    "terms": {"field": "distance", "size": 100}
                                },
                                "total_runners": {
                                    "sum_bucket": {"buckets_path": "distances>_count"}
                                }
                            }
                        }
                    }
                }
            )

            print("DEBUG - Réponse Elasticsearch :", response)

            data = []
            for bucket in response['aggregations']['competitions']['buckets']:
                competition_name = bucket['key']['competition_name']
                raw_date = bucket['key']['competition_date']
                competition_date = datetime.utcfromtimestamp(raw_date / 1000).strftime('%Y-%m-%d')
                level_abbreviation = bucket['key'].get('level', 'N/A')
                level = LEVEL_MAPPING.get(level_abbreviation, level_abbreviation)  # 🔹 Remplace le code par le texte complet
                department = bucket['key'].get('department', 'N/A')
                type_course = bucket['key'].get('type_course', 'N/A')
                ligue = bucket['key'].get('ligue', 'N/A')

                total_runners = sum(dist["doc_count"] for dist in bucket['distances']['buckets'])

                for distance_bucket in bucket['distances']['buckets']:
                    distance = distance_bucket['key']
                    runners_on_distance = distance_bucket['doc_count']

                    data.append({
                        "competition_date": competition_date,
                        "competition_name": competition_name,
                        "level": level,  # ✅ Affichage du niveau en texte lisible
                        "department": department,
                        "distance": distance,
                        "type_course": type_course,
                        "ligue": ligue,
                        "total_runners": total_runners,
                        "distance_runners": runners_on_distance
                    })

            result_text = f"{len(data)} résultat(s) trouvé(s)." if data else "Aucun résultat trouvé."
            return result_text, data

        except Exception as e:
            print(f"Erreur Elasticsearch : {e}")
            return "Erreur lors de la récupération des données.", []

    return "", []


@dash.callback(
    Output('search-department-page2', 'options'),
    Input('search-department-page2', 'id')
)
def load_departments(_):
    try:
        response = es.search(
            index=ELASTICSEARCH_INDEX,
            body={
                "size": 0,
                "aggs": {
                    "unique_departments": {
                        "terms": {"field": "department.keyword", "size": 1000}
                    }
                }
            }
        )

        departments = [bucket['key'] for bucket in response["aggregations"]["unique_departments"]["buckets"]]
        
        # Générer la liste des départements sous forme de {label, value}
        return [{"label": dept, "value": dept} for dept in departments]
    
    except Exception as e:
        print(f"Erreur Elasticsearch lors du chargement des départements : {e}")
        return []
@dash.callback(
    Output('search-competition-page2', 'options'),
    Input('search-competition-page2', 'id')
)
def load_competitions(_):
    try:
        response = es.search(
            index=ELASTICSEARCH_INDEX,
            body={
                "size": 0,
                "aggs": {
                    "unique_competitions": {
                        "terms": {"field": "competition_name.keyword", "size": 1000}
                    }
                }
            }
        )

        competitions = [bucket['key'] for bucket in response["aggregations"]["unique_competitions"]["buckets"]]
        
        # Générer la liste des compétitions sous forme de {label, value}
        return [{"label": comp, "value": comp} for comp in competitions]
    
    except Exception as e:
        print(f"Erreur Elasticsearch lors du chargement des compétitions : {e}")
        return []