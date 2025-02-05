import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from elasticsearch import Elasticsearch
from src.components import Navbar, Header, Footer
from src.utils.Utils import get_competitions, get_distances, get_filtered_data

# Enregistrement de la page
dash.register_page(__name__, path='/Histogram')

# Layout de la page
layout = html.Div([
    Header(),
    Navbar(),

    # 📌 Titre stylisé
    html.H1(
        ["Analyse des Compétitions ", html.Span("📊", style={"fontSize": "1.2em"})],
        style={
            'textAlign': 'center',
            'fontFamily': "'Poppins', sans-serif",
            'fontWeight': 'bold',
            'fontSize': '32px',
            'color': '#0d2366',  # Bleu foncé
            'textShadow': '2px 2px 4px rgba(0, 0, 0, 0.3)',
            'marginBottom': '30px'
        }
    ),

    html.Div([
        html.Label("Choisissez une compétition et une année", style={'fontFamily': "'Poppins', sans-serif"}),
        dcc.Dropdown(
            id="competition-dropdown",
            options=[],
            placeholder="Sélectionnez une compétition et une année",
            style={'width': '60%', 'margin': '10px auto'}  # Centrage et largeur réduite
        ),

        html.Label("Choisissez une distance", style={'fontFamily': "'Poppins', sans-serif"}),
        dcc.Dropdown(
            id="distance-dropdown",
            options=[],
            placeholder="Sélectionnez une distance",
            disabled=True,
            style={'width': '60%', 'margin': '10px auto'}  # Centrage et largeur réduite
        ),
    ], style={'textAlign': 'center'}),

    # 📊 Histogramme centré avec marges ajustées
    html.Div(
        dcc.Graph(id="histogram"),
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'margin': '30px auto',
            'width': '80%'  # Réduction de la taille
        }
    ),

    Footer()
])

# Callbacks
@callback(
    Output("competition-dropdown", "options"),
    Input("competition-dropdown", "id")
)
def load_competitions(_):
    competitions = get_competitions()
    return [{"label": name, "value": name} for name in competitions]

@callback(
    [Output("distance-dropdown", "options"),
     Output("distance-dropdown", "disabled")],
    Input("competition-dropdown", "value")
)
def update_distances(competition_with_year):
    if competition_with_year:
        parts = competition_with_year.split()
        year = parts[-1]
        competition_name = " ".join(parts[:-1])

        distances = get_distances(competition_name, year)
        if distances:
            options = [{"label": str(d), "value": d} for d in distances]
            return options, False
        
    return [], True

@callback(
    Output("histogram", "figure"),
    [Input("competition-dropdown", "value"),
     Input("distance-dropdown", "value")]
)
def update_histogram(competition_with_year, distance):
    if competition_with_year and distance:
        parts = competition_with_year.split()
        year = parts[-1]
        competition_name = " ".join(parts[:-1])

        data = get_filtered_data(competition_name, year, distance)

        if not data.empty:
            data = data.dropna(subset=["Minute_Time"])  # Suppression des NaN

            fig = px.histogram(
                data,
                x="Minute_Time",
                nbins=20,
                title=f"Distribution des temps pour {competition_name} {year} ({distance}m)",
                labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"}
            )
            fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
            return fig

    empty_data = pd.DataFrame({"Minute_Time": []})
    fig = px.histogram(
        empty_data,
        x="Minute_Time",
        nbins=1,
        title="Aucune donnée disponible",
        labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"}
    )
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    return fig
