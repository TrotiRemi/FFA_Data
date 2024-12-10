from dash import dcc

def DropdownHistogramme():
    histogram_options = [
        {'label': 'Histogramme général', 'value': 'G'},
        {'label': 'Histogramme hommes', 'value': 'H'},
        {'label': 'Histogramme femmes', 'value': 'F'},
        {'label': 'Histogramme comparatif', 'value': 'HF'}
    ]


    return dcc.Dropdown(
        id='histogram-dropdown',
        options=histogram_options,
        value='G',
        clearable=False
    )
