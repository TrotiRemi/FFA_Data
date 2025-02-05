import dash
from dash import html, dcc
from src.utils.Utils import generate_map
from src.components import Navbar, Header, Footer

# Enregistrement de la page
dash.register_page(__name__, path='/Map')

# Layout de la page Dash
layout = html.Div([
    Header(),
    Navbar(),
    
    # Titre principal avec l'icône 📍 bien centré
    html.Div([
        html.H1("Carte des coureurs par départements", style={
            'fontFamily': "'Poppins', sans-serif",
            'fontSize': '26px',
            'fontWeight': 'bold',
            'color': '#0d2366',
            'textShadow': '2px 2px 4px rgba(0, 0, 0, 0.3)',
            'display': 'inline-block',
            'marginRight': '10px',
            'verticalAlign': 'middle'  # Assure un bon alignement vertical
        }),
        html.Span("📍", style={
            'fontSize': '26px',  # Taille ajustée pour correspondre au texte
            'fontWeight': 'bold',
            'color': '#0d2366',
            'verticalAlign': 'middle',  # Assure un alignement parfait avec le texte
            'display': 'inline-block'
        })
    ], style={'textAlign': 'center', 'marginBottom': '15px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),

    # Carte des Coureurs par Département avec rognage latéral
    html.Div([
        dcc.Graph(
            id='map_coureurs',
            figure=generate_map(),
            style={'height': '450px', 'width': '55%', 'margin': 'auto', 'overflow': 'hidden'}  # Réduction de la largeur
        )
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),

    Footer()
])
