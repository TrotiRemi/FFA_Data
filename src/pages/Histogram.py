import dash
import random
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from src.components import Navbar, Header, Footer
from src.utils.Utils import get_competitions, get_distances, get_filtered_data

# Enregistrement de la page
dash.register_page(__name__, path='/Histogram')

# Récupération des compétitions dès le démarrage
competitions = get_competitions()
default_competition = random.choice(competitions) if competitions else None  # Choix aléatoire
default_year = default_competition.split()[-1] if default_competition else None
default_competition_name = " ".join(default_competition.split()[:-1]) if default_competition else None

# Récupération des distances pour cette compétition
default_distances = get_distances(default_competition_name, default_year) if default_competition else []
default_distance = random.choice(default_distances) if default_distances else None  # Choix aléatoire

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
            'color': '#0d2366',
            'textShadow': '2px 2px 4px rgba(0, 0, 0, 0.3)',
            'marginBottom': '30px'
        }
    ),

    html.Div([
        html.Label("Choisissez une compétition et une année", style={'fontFamily': "'Poppins', sans-serif"}),
        dcc.Dropdown(
            id="competition-dropdown",
            options=[{"label": name, "value": name} for name in competitions],
            value=default_competition,  # ✅ Valeur aléatoire par défaut
            placeholder="Sélectionnez une compétition et une année",
            style={'width': '60%', 'margin': '10px auto'}
        ),

        html.Label("Choisissez une distance", style={'fontFamily': "'Poppins', sans-serif"}),
        dcc.Dropdown(
            id="distance-dropdown",
            options=[{"label": str(d), "value": d} for d in default_distances],
            value=default_distance,  # ✅ Valeur aléatoire par défaut
            placeholder="Sélectionnez une distance",
            disabled=False if default_distances else True,  # Désactivé si pas de distance
            style={'width': '60%', 'margin': '10px auto'}
        ),
    ], style={'textAlign': 'center'}),

    # 📊 Histogramme avec barres collées
    html.Div(
        dcc.Graph(id="histogram"),
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'margin': '30px auto',
            'width': '100%',
            'maxWidth': '1100px',
            'height': '450px'
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
    return [{"label": name, "value": name} for name in get_competitions()]

@callback(
    [Output("distance-dropdown", "options"),
     Output("distance-dropdown", "disabled"),
     Output("distance-dropdown", "value")],  # ✅ Mise à jour de la valeur par défaut
    Input("competition-dropdown", "value")
)
def update_distances(competition_with_year):
    if competition_with_year:
        parts = competition_with_year.split()
        year = parts[-1]
        competition_name = " ".join(parts[:-1])

        distances = get_distances(competition_name, year)
        if distances:
            default_value = random.choice(distances)  # ✅ Choix aléatoire
            return [{"label": str(d), "value": d} for d in distances], False, default_value
        
    return [], True, None

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
                labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"},
                color_discrete_sequence=["#0d2366"]  # ✅ Barres en bleu foncé
            )

            fig.update_traces(
                marker_line_color="white",  # ✅ Contour blanc
                marker_line_width=1,  
                opacity=0.85  
            )

            fig.update_layout(
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                width=1100,
                height=450,
                xaxis_title="Temps (minutes)", 
                yaxis_title="Nombre de coureurs",
                plot_bgcolor="white",
                font=dict(family="Poppins, sans-serif", size=14),
                yaxis=dict(gridcolor="lightgrey", showline=True, linewidth=1, linecolor="black"),
                xaxis=dict(showline=True, linewidth=1, linecolor="black"),
                bargap=0  # ✅ Barres collées
            )

            return fig

    empty_data = pd.DataFrame({"Minute_Time": []})
    fig = px.histogram(
        empty_data,
        x="Minute_Time",
        nbins=1,
        title="Aucune donnée disponible",
        labels={"Minute_Time": "Temps (minutes)", "count": "Nombre de coureurs"},
        color_discrete_sequence=["#0d2366"]  # ✅ Barres en bleu foncé
    )

    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        width=1100,
        height=450,
        plot_bgcolor="white",
        font=dict(family="Poppins, sans-serif", size=14),
        yaxis=dict(gridcolor="lightgrey", showline=True, linewidth=1, linecolor="black"),
        xaxis=dict(showline=True, linewidth=1, linecolor="black"),
        bargap=0  # ✅ Barres collées
    )
    
    return fig
