import dash
from dash import html, dcc, Input, Output, State, dash_table
from src.components import Navbar, Header, Footer
import pandas as pd

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/')

# Charger le fichier CSV
dt = pd.read_csv('unlimited_results.csv')  # Remplace par ton fichier CSV
dt.loc[dt['competition_name'] == "Départementaux de cross-country cd14", 'distance'] = 8715
#print(dt[(dt['vitesse']<5) & (dt['rank'] != "-") & (dt['time'] != "-") & (dt['time'] != "- qi")])

# Liste des champs de recherche
search_fields = [
    {'id': 'search-name', 'placeholder': 'Nom', 'column': 'athlete', 'type': 'text'},
    {'id': 'search-club', 'placeholder': 'Club', 'column': 'club', 'type': 'text'},
    {'id': 'search-data', 'placeholder': 'Date (J/M/A(2 derniers chiffres))', 'column': 'date', 'type': 'text'},
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

# Fonction pour arrondir la vitesse
def format_speed(value):
    try:
        return f"{float(value):.1f}"
    except:
        return value  # En cas d'erreur, retourne la valeur d'origine

# Layout pour la page d'accueil
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Bienvenue sur la page d'accueil", style={'textAlign': 'center'}),

    # Barres de recherche
    html.Div([
        html.Div([
            dcc.Input(
                id=field['id'],
                type=field['type'],
                placeholder=field['placeholder'],
                style={'width': '70%', 'padding': '10px', 'margin-bottom': '10px'}
            )
            for field in search_fields
        ], style={'textAlign': 'center', 'margin-top': '20px'}),
        
        html.Button(
            'Rechercher',
            id='search-button',
            n_clicks=0,
            style={'padding': '10px 20px', 'background-color': '#007BFF', 'color': '#fff', 'border': 'none'}
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
                {"name": "Date", "id": "date"},
                {"name": "Course", "id": "competition_name"},
                {"name": "Temps", "id": "formatted_time"},
                {"name": "Vitesse", "id": "formatted_speed"},
                {"name": "Distance", "id": "distance"}
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

# Callback pour mettre à jour les résultats de recherche et le tableau
@dash.callback(
    [Output('search-result', 'children'),
     Output('result-table', 'data')],
    [Input('search-button', 'n_clicks')],
    [State(field['id'], 'value') for field in search_fields]  # Ajouter les valeurs dynamiquement
)
def update_search_result(n_clicks, *args):
    if n_clicks > 0:
        # Associer les colonnes aux valeurs des champs
        filters = {field['column']: value for field, value in zip(search_fields, args) if value}
        
        # Filtrage des données
        filtered_data = dt.copy()

        # Appliquer les filtres standards
        for column, value in filters.items():
            if column == 'distance_min':
                continue
            if column == 'distance_max':
                continue
            filtered_data = filtered_data[filtered_data[column].astype(str).str.contains(value, na=False, case=False)]

        # Filtrer par plage de distances
        if 'distance_min' in filters:
            filtered_data = filtered_data[filtered_data['distance'] >= float(filters['distance_min'])]
        if 'distance_max' in filters:
            filtered_data = filtered_data[filtered_data['distance'] <= float(filters['distance_max'])]

        # Préparer les résultats pour le tableau
        if not filtered_data.empty:
            filtered_data['formatted_time'] = filtered_data['Minute_Time'].apply(format_time_from_minutes)
            filtered_data['formatted_speed'] = filtered_data['vitesse'].apply(format_speed)

            table_data = filtered_data[['rank', 'athlete', 'club', 'date', 'competition_name', 'formatted_time', 'formatted_speed', 'distance']].to_dict('records')
        else:
            table_data = []

        # Résumé des résultats
        result_text = f"{len(filtered_data)} résultat(s) trouvé(s)." if not filtered_data.empty else "Aucun résultat trouvé."
        return result_text, table_data

    # Si aucun clic ou recherche vide
    return "", []
