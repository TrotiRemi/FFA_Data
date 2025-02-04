from dash import html, dcc

def Navbar():
    return html.Nav(
        children=[
            dcc.Link(
                [html.Img(src='/assets/run.svg', style={'width': '18px', 'margin-right': '5px'}), html.B(" Coureur")],
                href='/',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/flag.svg', style={'width': '18px', 'margin-right': '5px'}), html.B(" Course")],
                href='/Course',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/map-solid.svg', style={'width': '18px', 'margin-right': '5px'}), html.B(" Map")],
                href='/Map',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/chart-simple-solid.svg', style={'width': '18px', 'margin-right': '5px'}), html.B(" Histogramme")],
                href='/Histogram',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
        ],
        style={
            'padding': '5px 10px',             # Réduction de la hauteur
            'backgroundColor': '#0d2366',      # Bleu foncé
            'display': 'flex',                 # Alignement des liens sur une ligne
            'justify-content': 'space-around', # Espacement uniforme
            'borderBottom': '2px solid white', # Bordure fine blanche
            'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.2)'  # Ombre douce en bas
        }
    )
