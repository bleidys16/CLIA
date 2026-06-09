from django.urls import path
from apps.machine_learning.views import TrainModelView

urlpatterns = [
    path('train/', TrainModelView.as_view(), name='train-model'),
]
