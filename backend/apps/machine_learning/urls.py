from django.urls import path
from apps.machine_learning.views import TrainModelView, MetricasModeloMLView

urlpatterns = [
    path('train/', TrainModelView.as_view(), name='train-model'),
    path('model/metrics/', MetricasModeloMLView.as_view(), name='ml-metrics'),
]
