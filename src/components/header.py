from dash import html

def Header():
    return html.Header(
        children=[
            # Conteneur principal pour centrer le logo et les barres
            html.Div(
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'position': 'relative',
                    'width': '100%',
                },
                children=[
                    # Barres gauche (plus longues)
                    html.Div(
                        [
                            html.Hr(style={'border': '3px solid #0D1440', 'width': '45vw', 'margin': '0'}),
                            html.Hr(style={'border': '3px solid #0D1440', 'width': '45vw', 'margin': '0', 'margin-top': '5px'})
                        ],
                        style={'display': 'inline-block', 'verticalAlign': 'middle'}
                    ),

                    # Logo au centre avec fond blanc cassé et bord arrondi
                    html.Div(
                        html.Img(
                            src="/assets/logo.png",  # Remplacez par votre image
                            style={'height': '60px', 'display': 'block', 'margin': '0 auto'}
                        ),
                        style={
                            'backgroundColor': '#f8f9fa',  # Fond blanc cassé
                            'padding': '10px 25px',  # Ajustement de l'espace autour du logo
                            'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)',  # Ombre légère pour un effet propre
                            'borderRadius': '15px'  # Arrondi des bords sans contour
                        }
                    ),

                    # Barres droite (plus longues)
                    html.Div(
                        [
                            html.Hr(style={'border': '3px solid #0D1440', 'width': '45vw', 'margin': '0'}),
                            html.Hr(style={'border': '3px solid #0D1440', 'width': '45vw', 'margin': '0', 'margin-top': '5px'})
                        ],
                        style={'display': 'inline-block', 'verticalAlign': 'middle'}
                    ),
                ]
            )
        ],
        style={'backgroundColor': '#f8f9fa', 'padding': '20px 0', 'width': '100%'}
    )
