import dash
from dash import dcc, html
from dash import page_registry

# Initialisation de l'application
app = dash.Dash(__name__, use_pages=True, pages_folder="src/pages", suppress_callback_exceptions=True)

# Mise en page principale de l'application
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    dash.page_container
])

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True, port = 8060, host = '0.0.0.0')

app.layout = html.Div(
    children=[
        html.Div(id="content", style={'flex': '1'}),  # Le contenu prend toute la hauteur disponible
        Footer()  # Le footer est toujours en bas
    ],
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'minHeight': '100vh'  # La page doit au moins remplir toute la hauteur de l'écran
    }
)
