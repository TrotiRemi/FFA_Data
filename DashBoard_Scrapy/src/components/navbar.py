from dash import html, dcc

def Navbar():
    return html.Nav(
        children=[
            dcc.Link(
                [html.Img(src='/assets/run.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Coureur")],
                href='/',
                style={'color': 'Black', 'padding': '10px 20px', 'text-decoration': 'none', 'display': 'flex', 'align-items': 'center'}
            ),
            dcc.Link(
                [html.Img(src='/assets/flag.svg', style={'width': '20px', 'margin-right': '5px'}), html.B(" Course")],
                href='/Course',
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
