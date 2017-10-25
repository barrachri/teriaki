"""
Collection of routes for Teriaki.

routes.py

"""

from teriaki.views import welcome
from teriaki.views import upload


routes = [
    ('GET', '/', welcome),
    ('GET', '/upload', upload),
    ('POST', '/upload', upload),
]
