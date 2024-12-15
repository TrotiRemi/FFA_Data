import dash
from . import Coureur
from . import Course

# Enregistrement des pages
dash.register_page('Coureur', path='/', name='Coureur', layout=Coureur.layout)
dash.register_page('Course', path='/Course', name='Course', layout=Course.layout)