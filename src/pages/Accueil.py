import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

def Accueil():
    return html.Div(
        children=[
            # Image de fond en arrière-plan
            html.Img(
                src="/assets/fondaccueil3.png",
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

            # Contenu principal (bloc légèrement plus bas)
            html.Div(
                children=[
                    html.H1("Bienvenue sur notre Application FFA", style={
                        'color': 'white',
                        'textAlign': 'center',
                        'marginBottom': '10px',
                        'fontWeight': 'bold',
                        'fontFamily': "'Poppins', sans-serif"  # Police moderne
                    }),
                    html.P(
                        "Découvrez les statistiques et visualisations des courses officielles.",
                        style={
                            'color': 'white',
                            'textAlign': 'center',
                            'fontSize': '16px',
                            'fontFamily': "'Poppins', sans-serif"
                        }
                    ),

                    # Boutons organisés en colonne (même taille)
                    html.Div(
                        children=[
                            dcc.Link(
                                html.Button("Bibliothèque des coureurs", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '12px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px',
                                    'fontWeight': 'bold',
                                    'width': '200px',  # Taille uniforme
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '8px 0'
                                }),
                                href="/Coureur"
                            ),
                            dcc.Link(
                                html.Button("Rechercher une course", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '12px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '8px 0'
                                }),
                                href="/Course"
                            ),
                            dcc.Link(
                                html.Button("Histogramme des compétitions", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '12px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '8px 0'
                                }),
                                href="/Histogram"
                            ),
                            dcc.Link(
                                html.Button("Carte des coureurs par départements", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '12px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '8px 0'
                                }),
                                href="/Map"
                            ),
                        ],
                        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%'}
                    )
                ],
                style={
                    'padding': '30px',  # Réduction du padding pour diminuer la hauteur
                    'backgroundColor': 'rgba(13, 35, 102, 0.85)',  # Fond semi-transparent pour lisibilité
                    'borderRadius': '20px',  # Coins arrondis
                    'boxShadow': '0px 6px 15px rgba(0, 0, 0, 0.3)',  # Ombre plus marquée
                    'maxWidth': '400px',  # Largeur maintenue
                    'margin': 'auto',
                    'marginTop': '180px',  # Bloc toujours abaissé
                    'textAlign': 'center'
                }
            )
        ],
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'justifyContent': 'start',  # Garde un alignement propre
            'height': '100vh',
            'width': '100vw',
            'paddingTop': '60px'  # Ajoute encore un léger décalage vers le bas
        }
    )

layout = Accueil()
