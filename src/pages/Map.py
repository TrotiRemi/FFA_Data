import dash
from dash import html, dcc
from src.utils.Utils import generate_map  # Assure-toi que le chemin est correct
from src.components import Navbar, Header, Footer

# Enregistrement de la page
dash.register_page(__name__, path='/Map')

# Layout de la page Dash
layout = html.Div([
    Header(),
    Navbar(),
    html.H1("Carte des Départements Français"),
    dcc.Graph(
        id='map',
        figure=generate_map()  # Appelle la fonction de la carte depuis utils
    ),
    Footer()
])
