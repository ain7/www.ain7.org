
from django.db.models import Q

FILTERS = (
)

try:
     from filters_local import FILTERS
except ImportError:
    pass

