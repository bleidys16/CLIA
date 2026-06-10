# backend/apps/etl/urls.py
# Rutas internas de la app ETL.
# Importamos la vista que ejecuta el pipeline.

from django.urls import path
from .views import RunETLView, ETLLogListView, ResetDataView, AuthMeView, DashboardAnalyticsView

urlpatterns = [
    path('run/', RunETLView.as_view(), name='etl-run'),
    path('logs/', ETLLogListView.as_view(), name='etl-logs'),
    path('reset/', ResetDataView.as_view(), name='etl-reset'),
    path('auth/me/', AuthMeView.as_view(), name='etl-auth-me'),
    path('analytics/dashboard/', DashboardAnalyticsView.as_view(), name='etl-analytics-dashboard'),
]