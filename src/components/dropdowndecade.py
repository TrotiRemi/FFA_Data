from dash import dcc

def DropdownDecade():
    decades = ['1960s', '1970s', '1980s', '1990s', '2000s', '2010s']

    return dcc.Dropdown(
        id='decade-dropdown',
        options=[{'label': decade, 'value': decade} for decade in decades],
        value='1960s', 
        clearable=False
    )

