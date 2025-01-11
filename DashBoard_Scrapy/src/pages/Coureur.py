import dash
from dash import html, dcc, Input, Output, State, dash_table
from src.components import Navbar, Header, Footer
import pandas as pd

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/')

# Charger le fichier CSV
dt = pd.read_csv('Docker_results_laver.csv')  # Remplace par ton fichier CSV
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

layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Chercher un coureur", style={'textAlign': 'center'}),

    # Barres de recherche
    html.Div([
        # Autres champs de recherche
        html.Div([
            dcc.Input(
                id=field['id'],
                type=field['type'],
                placeholder=field['placeholder'],
                style={'width': '70%', 'padding': '10px', 'margin-bottom': '10px'}
            )
            for field in search_fields if field['column'] not in ['distance_min', 'distance_max', 'date']
        ], style={'textAlign': 'center', 'margin-top': '20px'}),

        # Distance minimale et maximale sur la même ligne
        html.Div([
            html.Label("Distance :", style={
                    'font-weight': 'bold',
                    'margin-right': '10px',
                    'align-self': 'center'  # Assure l'alignement vertical avec les menus déroulants
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
                'display': 'flex',  # Affiche les éléments horizontalement
                'align-items': 'center',  # Aligne verticalement tous les éléments
                'margin-top': '5px',
                'margin-left': '9%'
            }),

        # Menus déroulants pour les dates alignés et espacés
        html.Div([
            html.Div([
                html.Label("Date :", style={
                    'font-weight': 'bold',
                    'margin-right': '10px',
                    'align-self': 'center'  # Assure l'alignement vertical avec les menus déroulants
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
                'display': 'flex',  # Affiche les éléments horizontalement
                'align-items': 'center',  # Aligne verticalement tous les éléments
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
                {"name": "Date", "id": "date"},
                {"name": "Course", "id": "competition_name"},
                {"name": "Temps", "id": "formatted_time"},
                {"name": "Vitesse", "id": "formatted_speed"},
                {"name": "Distance", "id": "distance"}
            ],
            data=[],  # Données initialement vides
            style_table={'margin-top': '20px', 'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',
                'padding': '10px',
                'whiteSpace': 'normal',  # Permet les retours à la ligne
                'overflow': 'hidden',  # Empêche les débordements
                'textOverflow': 'ellipsis',  # Ajoute des "..." pour le texte coupé (utile pour éviter des débordements horizontaux)
                'maxWidth': '150px',  # Largeur maximale fixe pour chaque colonne
                'minWidth': '100px',  # Largeur minimale pour assurer une lisibilité
            },
            style_data={
                'height': 'auto',  # Ajuste automatiquement la hauteur des cellules pour le texte
            },
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
    [State(field['id'], 'value') for field in search_fields if field['column'] != 'date'] + 
    [State('search-day', 'value'), State('search-month', 'value'), State('search-year', 'value')]
)
def update_search_result(n_clicks, *args):
    if n_clicks > 0:
        # Associer les colonnes aux valeurs des champs
        filters = {field['column']: value for field, value in zip(search_fields, args[:len(search_fields) - 1]) if value}

        # Récupérer les valeurs des menus déroulants pour les dates
        day, month, year = args[-3:]

        # Si un ou plusieurs composants de la date sont renseignés
        if day or month or year:
            # Convertir le champ 'date' en parties (jour, mois, année)
            dt['day'] = dt['date'].str.slice(0, 2)  # Extraire le jour
            dt['month'] = dt['date'].str.slice(3, 5)  # Extraire le mois
            dt['year'] = dt['date'].str.slice(6, 8)  # Extraire l'année (2 derniers chiffres)

            # Ajouter les filtres partiels sur les jours, mois, années
            if day:
                filters['day'] = day
            if month:
                filters['month'] = month
            if year:
                filters['year'] = year

        # Filtrage des données
        filtered_data = dt.copy()
        for column, value in filters.items():
            filtered_data = filtered_data[filtered_data[column].astype(str).str.contains(value, na=False, case=False)]

        # Supprimer les colonnes temporaires pour éviter des problèmes
        filtered_data = filtered_data.drop(columns=['day', 'month', 'year'], errors='ignore')

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
