import dash
from dash import html, dcc, Input, Output, State, dash_table
from src.components import Navbar, Header, Footer
import pandas as pd

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/Course')

# Charger le fichier CSV
dt = pd.read_csv('resultat_course.csv')  # Remplace par ton fichier CSV

# Champs de recherche
search_fields = [
    {'id': 'search-name', 'placeholder': 'Nom de la Course', 'column': 'competition_name', 'type': 'text'},
    {'id': 'search-level', 'placeholder': 'Niveau', 'column': 'level', 'type': 'text'},
    {'id': 'search-date', 'placeholder': 'Date (J/M/A(2 derniers chiffres))', 'column': 'date', 'type': 'text'},
    {'id': 'search-type', 'placeholder': 'Type de competition', 'column': 'competition_type', 'type': 'text'},
    {'id': 'search-dep', 'placeholder': 'Département', 'column': 'departement', 'type': 'number'}
]

# Layout
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Bienvenue sur la page des Courses", style={'textAlign': 'center'}),

    # Champs de recherche pour Page 2
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

    # Tableau des résultats pour Page 2
    html.Div(
        dash_table.DataTable(
            id='result-table-page2',
            columns=[
                {"name": "Date", "id": "date"},
                {"name": "Nom", "id": "competition_name"},
                {"name": "Lieu", "id": "location"},
                {"name": "Ligue", "id": "ligue"},
                {"name": "Type", "id": "competition_type"},
                {"name": "Niveau", "id": "level"},
                {"name": "Distances", "id": "distance"},
                {"name": "Nombre de Coureur", "id": "Nombre_Coureur"}
            ],
            data=[],  # Données initialement vides
            style_table={'margin-top': '20px', 'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={'fontWeight': 'bold'}
        ),
        style={'width': '80%', 'margin': '0 auto'}
    ),
    Footer()
])


@dash.callback(
    [Output('search-result-page2', 'children'),
     Output('result-table-page2', 'data')],
    [Input('search-button-page2', 'n_clicks')],
    [State(field['id'] + '-page2', 'value') for field in search_fields]
)
def update_page2(n_clicks, *args):
    if n_clicks > 0:
        # Associer les colonnes aux valeurs des champs
        filters = {field['column']: value for field, value in zip(search_fields, args) if value}

        # Filtrage des données
        filtered_data = dt.copy()
        for column, value in filters.items():
            filtered_data = filtered_data[
                filtered_data[column].astype(str).str.contains(str(value), case=False, na=False)
            ]

        # Résumé des résultats
        result_text = f"{len(filtered_data)} résultat(s) trouvé(s)." if not filtered_data.empty else "Aucun résultat trouvé."
        return result_text, filtered_data.to_dict('records')

    return "", []

