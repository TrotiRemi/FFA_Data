import dash
from dash import html, dcc, Input, Output, State, dash_table
from src.components import Navbar, Header, Footer
from pymongo import MongoClient
import pandas as pd

# Enregistrement de la page d'accueil
dash.register_page(__name__, path='/')

# Charger le fichier CSV
#dt = pd.read_csv('FFA/Course2.csv')  # Remplace par ton fichier CSV
#dt.loc[dt['competition_name'] == "Départementaux de cross-country cd14", 'distance'] = 8715
#print(dt[(dt['vitesse']<5) & (dt['rank'] != "-") & (dt['time'] != "-") & (dt['time'] != "- qi")])

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
        # Construire les filtres pour MongoDB
        filters = {}
        if name:  # Nom
            filters['athlete'] = {'$regex': name, '$options': 'i'}
        if club:  # Club
            filters['club'] = {'$regex': club, '$options': 'i'}
        if distance_min:  # Distance minimale
            filters['distance'] = {'$gte': float(distance_min)}
        if distance_max:  # Distance maximale
            if 'distance' in filters:
                filters['distance']['$lte'] = float(distance_max)
            else:
                filters['distance'] = {'$lte': float(distance_max)}

        # Gestion des dates
        if day or month or year:
            date_filter = ""
            if day:
                date_filter += f"{day:02}/"
            if month:
                date_filter += f"{month:02}/"
            if year:
                date_filter += f"{year:02}"
            filters['competition_date'] = {'$regex': date_filter, '$options': 'i'}

        # Obtenir les données de MongoDB
        filtered_data = get_data_from_mongo(filters)

        # Préparer les résultats pour le tableau
        if not filtered_data.empty:
            table_data = filtered_data[['rank', 'athlete', 'club', 'competition_date', 'competition_name', 'vitesse', 'distance']].to_dict('records')
        else:
            table_data = []

        # Résumé des résultats
        result_text = f"{len(filtered_data)} résultat(s) trouvé(s)." if not filtered_data.empty else "Aucun résultat trouvé."
        return result_text, table_data

    return "", []
