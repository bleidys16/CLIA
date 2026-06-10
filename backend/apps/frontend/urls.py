from django.urls import path
from django.views.generic import RedirectView
from .views import login_view, dashboard_view, etl_view, pacientes_view, ml_modeling_view
from apps.analytics.views import DashboardKPIsView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('etl/', etl_view, name='etl'),
    path('pacientes/', pacientes_view, name='pacientes'),
    path('ml-modeling/', ml_modeling_view, name='ml-modeling'),
    path('dashboard/kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
]
