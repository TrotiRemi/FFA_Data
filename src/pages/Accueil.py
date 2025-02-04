import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

def Accueil():
    return html.Div(
        children=[
            # Image de fond en arrière-plan
            html.Img(
                src="/assets/fondaccueil.png",
                style={
                    'position': 'fixed',  # Fixe l'image en arrière-plan
                    'top': '0',
                    'left': '0',
                    'width': '100vw',  # Largeur complète de l'écran
                    'height': '100vh',  # Hauteur complète de l'écran
                    'zIndex': '-1',  # Met l'image derrière le contenu
                    'objectFit': 'cover'  # Assure un bon redimensionnement
                }
            ),

            # Contenu principal
            html.Div(
                children=[
                    html.H1("Bienvenue sur notre Application FFA", style={
                        'color': 'white',
                        'textAlign': 'center',
                        'marginBottom': '10px',
                        'fontWeight': 'bold'
                    }),
                    html.P(
                        "Découvrez les statistiques et visualisations des courses officielles.",
                        style={'color': 'white', 'textAlign': 'center', 'fontSize': '16px'}
                    ),
                    html.Div(
                        dcc.Link(
                            html.Button("Explorer", style={
                                'backgroundColor': '#FFD700',
                                'color': '#0d2366',
                                'padding': '10px 20px',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer',
                                'fontSize': '16px',
                                'fontWeight': 'bold'
                            }),
                            href="/Course"
                        ),
                        style={'textAlign': 'center', 'marginTop': '20px'}
                    )
                ],
                style={
                    'padding': '50px',
                    'backgroundColor': 'rgba(13, 35, 102, 0.85)',  # Fond semi-transparent pour lisibilité
                    'borderRadius': '15px',
                    'boxShadow': '0px 4px 10px rgba(0, 0, 0, 0.2)',
                    'maxWidth': '600px',
                    'margin': 'auto',
                    'marginTop': '50px',
                    'textAlign': 'center'
                }
            )
        ],
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'justifyContent': 'center',
            'height': '100vh',
            'width': '100vw'
        }
    )

layout = Accueil()
