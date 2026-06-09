from django.urls import path
from django.views.generic import RedirectView
from .views import dashboard_view, etl_view
from apps.analytics.views import DashboardKPIsView

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('etl/', etl_view, name='etl'),
    path('dashboard/kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
]
