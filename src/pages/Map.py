import dash
from dash import html, dcc
from src.utils.Utils import generate_map, generate_competition_map
from src.components import Navbar, Header, Footer

# Enregistrement de la page
dash.register_page(__name__, path='/Map')

# Layout de la page Dash
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Carte des Départements Français"),
    
    # Première carte : Coureurs par département
    html.Div([
        html.H2("Carte des Coureurs par Département"),
        dcc.Graph(
            id='map_coureurs',
            figure=generate_map() 
        )
    ]),

    # Deuxième carte : Compétitions par département
    html.Div([
        html.H2("Carte des Compétitions par Département"),
        dcc.Graph(
            id='map_competitions',
            figure=generate_competition_map() 
        )
    ]),

    Footer()
])
