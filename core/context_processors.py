# core/context_processors.py
from . import constants

def constants_context(request):
    return {"C": constants}
