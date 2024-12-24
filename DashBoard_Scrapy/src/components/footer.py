from dash import html

def Footer():
    return html.Footer(
        children=[
            html.P("Rémi LOCQUETTE - Lorenzo Vidy - Romain Alves Ferreira 2024-2025", style={'textAlign': 'center', 'color' : 'black'}),
            html.P("Ce Projet est possible grâce au données de la ffa", style={'textAlign': 'center', 'color' : 'black'}),
        ],
        style={'padding': '10px', 'backgroundColor': 'Bronze'}
    )
