import dash
from . import Coureur
from . import Course
from . import Map
from . import Histogram

# Enregistrement des pages
dash.register_page('Coureur', path='/', name='Coureur', layout=Coureur.layout)
dash.register_page('Course', path='/Course', name='Course', layout=Course.layout)
dash.register_page('Map', path='/Map', name='Map', layout=Map.layout)
dash.register_page('Histogram', path='/Histogram', name='Histogram', layout=Histogram.layout)