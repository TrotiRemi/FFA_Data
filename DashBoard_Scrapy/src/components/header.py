from dash import html

def Header():
    return html.Header(
        children=[
            html.H1("Projet Scrap : Les coureurs de cross", style={'textAlign': 'center', 'color': 'White'}),
        ],
        style={'padding': '20px', 'backgroundColor': 'Black'}
    )
