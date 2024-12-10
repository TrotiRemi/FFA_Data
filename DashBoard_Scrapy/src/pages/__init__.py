import dash
from . import home

# Enregistrement des pages
dash.register_page('search', path='/', name='search', layout=home.layout)