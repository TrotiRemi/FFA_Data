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

            # Contenu principal (bloc fixe, légèrement descendu)
            html.Div(
                children=[
                    html.H1("Bienvenue sur notre Application FFA", style={
                        'color': 'white',
                        'textAlign': 'center',
                        'marginBottom': '8px',  # Réduction de la marge
                        'fontWeight': 'bold',
                        'fontFamily': "'Poppins', sans-serif"
                    }),
                    html.P(
                        "Découvrez les statistiques et visualisations des courses officielles.",
                        style={
                            'color': 'white',
                            'textAlign': 'center',
                            'fontSize': '15px',  # Légère réduction de la taille du texte
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
                                    'padding': '10px 0',  # Légère réduction du padding
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '15px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '6px 0'  # Moins d'espace entre les boutons
                                }),
                                href="/Coureur"
                            ),
                            dcc.Link(
                                html.Button("Rechercher une course", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '10px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '15px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '6px 0'
                                }),
                                href="/Course"
                            ),
                            dcc.Link(
                                html.Button("Histogramme des compétitions", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '10px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '15px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '6px 0'
                                }),
                                href="/Histogram"
                            ),
                            dcc.Link(
                                html.Button("Carte des coureurs par départements", style={
                                    'backgroundColor': 'white',
                                    'color': '#0d2366',
                                    'padding': '10px 0',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '15px',
                                    'fontWeight': 'bold',
                                    'width': '200px',
                                    'textAlign': 'center',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'margin': '6px 0'
                                }),
                                href="/Map"
                            ),
                        ],
                        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'width': '100%'}
                    )
                ],
                style={
                    'position': 'fixed',  # Fixe le bloc en place
                    'top': '55%',  # Descend légèrement le bloc
                    'left': '50%',  # Centre horizontalement
                    'transform': 'translate(-50%, -50%)',  # Ajuste le centrage
                    'padding': '25px',  # Réduction du padding pour une hauteur plus compacte
                    'backgroundColor': 'rgba(13, 35, 102, 0.85)',  # Fond semi-transparent
                    'borderRadius': '20px',  # Coins arrondis
                    'boxShadow': '0px 6px 15px rgba(0, 0, 0, 0.3)',  # Ombre plus marquée
                    'maxWidth': '400px',
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
