# backend/apps/etl/urls.py
# Rutas internas de la app ETL.
# Importamos la vista que ejecuta el pipeline.

from django.urls import path
from .views import RunETLView

urlpatterns = [
    path('run/', RunETLView.as_view(), name='etl-run'),
]