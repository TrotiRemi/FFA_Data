import dash
from dash import dcc, html
from dash import page_registry

# Initialisation de l'application
app = dash.Dash(__name__, use_pages=True, pages_folder="src/pages")

# Mise en page principale de l'application
app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    dash.page_container
])

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True, port = 8060)
