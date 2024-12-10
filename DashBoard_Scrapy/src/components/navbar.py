from dash import html, dcc

def Navbar():
    return html.Nav(
        children=[
            dcc.Link(
                [html.Img(src='/assets/house-solid.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Home")],
                href='/',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/chart-simple-solid.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Histogram Boston 2019")],
                href='/histogram',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/chart-line-solid.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Répartition des records des 8000 meilleurs coureurs")],
                href='/graph',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/globe-solid.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Carte des meilleurs pays au marathon")],
                href='/map',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/arrow-up-solid.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Évolution des records enregistrés des pays au marathon")],
                href='/evolution',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
        ],
        style={
            'padding': '10px',
            'backgroundColor': 'White',      # Couleur de fond de la navbar
            'display': 'flex',               # Alignement des liens sur une ligne
            'justify-content': 'space-around',# Espacement uniforme des liens
            'borderBottom': '2px solid black' # Barre noire fine en bas de la navbar
        }
    )
