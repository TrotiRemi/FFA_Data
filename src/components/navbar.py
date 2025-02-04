from dash import html, dcc

def Navbar():
    return html.Nav(
        children=[
            dcc.Link(
                [html.Img(src='/assets/run.svg', style={'width': '18px', 'margin-right': '5px', 'filter': 'invert(1)'}), 
                 html.B(" Coureur", style={'font-family': "'Poppins', sans-serif"})],
                href='/',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/flag.svg', style={'width': '18px', 'margin-right': '5px', 'filter': 'invert(1)'}), 
                 html.B(" Course", style={'font-family': "'Poppins', sans-serif"})],
                href='/Course',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/map-solid.svg', style={'width': '18px', 'margin-right': '5px', 'filter': 'invert(1)'}), 
                 html.B(" Map", style={'font-family': "'Poppins', sans-serif"})],
                href='/Map',
                style={'color': 'white', 'padding': '8px 15px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/chart-simple-solid.svg', style={'width': '18px', 'margin-right': '5px', 'filter': 'invert(1)'}), 
                 html.B(" Histogramme", style={'font-family': "'Poppins', sans-serif"})],
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
            'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.2)',  # Ombre douce en bas
            'font-family': "'Poppins', sans-serif"  # Police moderne
        }
    )
