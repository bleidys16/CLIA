from django.urls import path
from apps.analytics.views import DashboardKPIsView

urlpatterns = [
    path('kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
]
