from django.urls import path
from django.views.generic import RedirectView
from .views import login_view, dashboard_view, etl_view
from apps.analytics.views import DashboardKPIsView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('etl/', etl_view, name='etl'),
    path('dashboard/kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
]
