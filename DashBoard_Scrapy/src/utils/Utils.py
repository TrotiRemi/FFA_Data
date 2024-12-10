import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
import os
import plotly.express as px
import plotly.graph_objects as go


#print histogramme


def print_histogramme(Mt, bins, col, titre):

    Mt["Result_hr_numeric"] = Mt[col]
    XR = Mt["Result_hr_numeric"].apply(convert_to_hours)
    plt.hist(XR, bins=bins)
    plt.title(titre)
    plt.xlabel('Time (hours)')
    plt.ylabel('Number')
    plt.legend()
    plt.savefig(os.path.join('Images', f'{titre}.png'))
    plt.close()

    return


#print histogramme d'un genre


def print_gender_histogramme(Mt, bins, col, titre, gender):
    Mt["Result_hr_numeric"] = Mt[col].apply(convert_to_hours)
    
    men_times = Mt[Mt['Gender'] == gender[0]]["Result_hr_numeric"]
    women_times = Mt[Mt['Gender'] == gender[1]]["Result_hr_numeric"]
    
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=men_times,
        nbinsx=bins,
        name="Hommes",
        marker_color='blue',
        opacity=1
    ))

    fig.add_trace(go.Histogram(
        x=women_times,
        nbinsx=bins,
        name="Femmes",
        marker_color='pink',
        opacity=0.7
    ))

    fig.update_layout(
        title=titre,
        xaxis_title="Temps (Heure)",
        yaxis_title="Nombre de coureurs",
        barmode="overlay",
        legend_title="Genre"
    )
    
    return fig


#print histogramme des genres


import plotly.express as px

def print_one_gender_histogramme(Mt, bins, col, titre, gender, color, label):
    Mt["Result_hr_numeric"] = Mt[col].apply(convert_to_hours)
    
    fig = px.histogram(
        Mt[Mt['Gender'] == gender],
        x="Result_hr_numeric",
        nbins=bins,
        title=titre,
        labels={"Result_hr_numeric": "Temps (Heure)"}
    )
    fig.update_traces(marker_color=color, name=label)
    
    fig.update_layout(
        xaxis_title="Temps (Heure)",
        yaxis_title=f"Nombre de {label}",
        legend_title="Genre"
    )
    
    return fig


#Print le meilleur temps


def Meilleur_Temps(Genre,Mt):
    Women = Mt[Mt["Gender"]==Genre]
    Best = np.min(Women['Time'].apply(convert_to_hours))
    print(Best)


#Print le pire temps


def Pire_Temps(Genre,Mt):
    Women = Mt[Mt["Gender"]==Genre]
    Worst = np.max(Women['Time'].apply(convert_to_hours))
    print(Worst)


#Convertisseur de string d'année en seconde


def convertir_temps_en_secondes(temps_str):
        heures, minutes, secondes = map(int, temps_str.split(':'))
        return heures * 3600 + minutes * 60 + secondes


#print map


def print_map(Mt, geo_data, coords, legend, bins, Map_Name, years=[0, 0]):
    if years != [0, 0]:
        Mt['Date'] = pd.to_datetime(Mt['Date'], format='%d.%m.%Y')
        Mt['Year'] = Mt['Date'].dt.year
        Mt = Mt[(Mt['Year'] < years[1]) & (Mt['Year'] >= years[0])]

    country_counts = Mt['Country'].value_counts().reset_index()
    country_counts.columns = ['ISO_A3', 'Frequency']

    for feature in geo_data['features']:
        iso_a3 = feature['properties']['ISO_A3']
        frequency = country_counts[country_counts['ISO_A3'] == iso_a3]['Frequency'].values
        feature['properties']['Frequency'] = int(frequency[0]) if len(frequency) > 0 else '0'

    map = folium.Map(location=coords, tiles='OpenStreetMap', zoom_start=1)

    choropleth = folium.Choropleth(
        geo_data=geo_data,
        name='choropleth',
        data=country_counts,
        columns=['ISO_A3', 'Frequency'],
        key_on='feature.properties.ISO_A3',
        fill_color='YlGn',
        fill_opacity=0.9,
        line_opacity=0.2,
        legend_name=legend,
        nan_fill_color='white',
        bins=bins
    ).add_to(map)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['ADMIN', 'Frequency'],
            aliases=['Nom du pays', 'Fréquence'],
            labels=True,
            sticky=False
        )
    )

    folium.LayerControl().add_to(map)

    map.save(os.path.join('Images', 'Map_difference', Map_Name))


#print graph évolution course


def print_graph(Mt):

    Mt['Date'] = pd.to_datetime(Mt['Date'], format='%d.%m.%Y')
    Mt['Year'] = Mt['Date'].dt.year
    MY = Mt['Year'].value_counts().sort_index().reset_index()
    MY.columns = ['Year', 'Count']
    MY['Year'] = pd.to_datetime(MY['Year'], format='%Y')
    fig, ax = plt.subplots()
    ax.plot(MY["Year"], MY["Count"])
    axe_x = pd.date_range(start='1963', end=MY['Year'].max(), freq='5Y')
    ax.set_xticks(axe_x)
    ax.set_xticklabels(axe_x.strftime("%Y"))
    plt.savefig(os.path.join('Images', 'graph_evolution_course.png'))
    plt.close()


#Graph évolution course pays


def map_evolve(Mt, geo_data, coords, legend, Map_Name,bins):

    Mt['Date'] = pd.to_datetime(Mt['Date'], format='%d.%m.%Y')
    Mt['Year'] = Mt['Date'].dt.year
    Mt = Mt.sort_values(by="Date")
    Mt1 = Mt[: len(Mt)//2 + 1]
    Mt2 = Mt[len(Mt)//2 + 1:]
    country_counts1 = Mt1['Country'].value_counts().reset_index()
    country_counts1.columns = ['ISO_A3', 'Frequency']
    country_counts2 = Mt2['Country'].value_counts().reset_index()
    country_counts2.columns = ['ISO_A3', 'Frequency']
    country_evolve = country_counts2.merge(country_counts1, on='ISO_A3', suffixes=('_2', '_1'))
    country_evolve['evolution'] = country_evolve['Frequency_2'] - country_evolve['Frequency_1']
    country_evolve = country_evolve[['ISO_A3', 'evolution']]

    # Ajouter la fréquence à chaque pays dans geo_data
    for feature in geo_data['features']:
        iso_a3 = feature['properties']['ISO_A3']
        frequency = country_evolve[country_evolve['ISO_A3'] == iso_a3]['evolution'].values
        feature['properties']['evolution'] = int(frequency[0]) if len(frequency) > 0 else '0'
    map = folium.Map(location=coords, tiles='OpenStreetMap', zoom_start=1)
    
    Choropleth = folium.Choropleth(
        geo_data=geo_data,
        name='choropleth',
        data=country_evolve,
        columns=['ISO_A3', 'evolution'],
        key_on='feature.properties.ISO_A3',
        fill_color='RdYlGn',
        fill_opacity=0.9,
        line_opacity=0.2,
        legend_name=legend,
        nan_fill_color='white',
        bins=bins
    ).add_to(map)
    
    Choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=['ADMIN', 'evolution'],
            aliases=['Nom du pays', 'Fréquence'],
            labels=True,
            sticky=False
        )
    )

    folium.LayerControl().add_to(map)

    map.save(os.path.join('Images','Map_evolution', Map_Name))


#convertie un temps en heure


def convert_to_hours(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h + m / 60 + s / 3600


#print un coureur


def coureur(Mt,name):
    return Mt[Mt['Name'].str.contains(name, case=False, na=False)]


#Créée un graph


def Graph(Mt):
    Mt['Date'] = pd.to_datetime(Mt['Date'], format='%d.%m.%Y')
    Mt['Year'] = Mt['Date'].dt.year
    MY = Mt['Year'].value_counts().sort_index().reset_index()
    MY.columns = ['Year', 'Count']
    MY['Year'] = pd.to_datetime(MY['Year'], format='%Y')
    axe_x = pd.date_range(start='1963', end=MY['Year'].max(), freq='5YE')
    fig = px.line(
        MY,
        'Year',
        y='Count',
        title="Répartition des records des 8000 meilleurs coureurs",
        labels={'Year': 'Année', 'count': 'Nombre de coureurs'}
    )
    fig.update_layout(
        xaxis_title="Temps (Heure)",
        yaxis_title="Nombre de coureurs",
        legend_title="Gender"
    )
    
    return fig

#Crée un histogramme


def hist(Mt):
    Mt["Result_hr_numeric"] = Mt['Result_hr']
    XR = Mt["Result_hr_numeric"].apply(convert_to_hours)
    
    fig = px.histogram(
        XR,
        x='Result_hr_numeric',
        nbins=50,
        title='Histogramme des temps de course au marathon de Boston 2019',
        labels={'Result_hr_numeric': 'Temps (Heure)', 'count': 'Nombre de coureurs'}
    )

    fig.update_layout(
        xaxis_title="Temps (Heure)",
        yaxis_title="Nombre de coureurs",
        legend_title="Gender"
    )
    
    return fig