from dash import html

def Footer():
    return html.Footer(
        children=[
            html.P("Rémi LOCQUETTE - Lorenzo Vidy - Romain Alves Ferreira 2024-2025", 
                   style={'textAlign': 'center', 'color': 'white', 'margin': '3px', 
                          'fontFamily': "'Poppins', sans-serif", 'fontSize': '12px', 
                          'fontWeight': 'bold'}),
            html.P("Ce Projet est possible grâce aux données de la FFA", 
                   style={'textAlign': 'center', 'color': 'white', 'margin': '3px', 
                          'fontFamily': "'Poppins', sans-serif", 'fontSize': '12px', 
                          'fontWeight': 'bold'}),
        ],
        style={
            'position': 'fixed',             # Fixe le footer même si la page est grande
            'bottom': '0',                   # Toujours en bas
            'left': '0',                     # Aligné à gauche
            'width': '100%',                 # Prend toute la largeur
            'padding': '5px 10px',           # Barre fine
            'minHeight': '30px',             # Assure une hauteur fine
            'backgroundColor': '#0d2366',    # Bleu foncé comme la navbar
            'borderTop': '2px solid white',  # Bordure blanche en haut
            'textAlign': 'center',           # Centrage du texte
            'fontFamily': "'Poppins', sans-serif",
            'zIndex': '1000'                 # S'assure qu'il reste au-dessus des autres éléments
        }
    )
