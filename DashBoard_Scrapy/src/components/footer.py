from dash import html

def Footer():
    return html.Footer(
        children=[
            html.P("Rémi LOCQUETTE 2024-2025", style={'textAlign': 'center', 'color' : 'black'}),
        ],
        style={'padding': '10px', 'backgroundColor': 'Bronze'}
    )
