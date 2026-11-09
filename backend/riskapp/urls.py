from django.urls import path
from .views import (
    LoginView, LogoutView, UserInfoView,
    FileUploadView, DataPreviewView, DeleteAllDataView, DataStatsView,
    TrainModelsView, TrainingHistoryView,
    PredictView, BatchPredictView, ModelDetailView, SHAPView,
    DashboardDataView, ExportReportView,
    AlertListView, AlertReviewView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserInfoView.as_view(), name='user-info'),
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('preview/', DataPreviewView.as_view(), name='preview'),
    path('delete-all/', DeleteAllDataView.as_view(), name='delete-all'),
    path('stats/', DataStatsView.as_view(), name='stats'),
    path('train/', TrainModelsView.as_view(), name='train'),
    path('training-history/', TrainingHistoryView.as_view(), name='training-history'),
    path('predict/', PredictView.as_view(), name='predict'),
    path('batch-predict/', BatchPredictView.as_view(), name='batch-predict'),
    path('model-detail/<str:model_name>/', ModelDetailView.as_view(), name='model-detail'),
    path('shap/', SHAPView.as_view(), name='shap'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard'),
    path('export-report/', ExportReportView.as_view(), name='export-report'),
    path('alerts/', AlertListView.as_view(), name='alert-list'),
    path('alerts/<int:alert_id>/review/', AlertReviewView.as_view(), name='alert-review'),
]
