from django.urls import path
from .views import FileUploadView, TrainModelsView, PredictView, DashboardDataView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('train/', TrainModelsView.as_view(), name='train'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard'),
]
