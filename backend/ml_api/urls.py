from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.prediction, name='prediction'),
    path('history/', views.prediction_history, name='prediction_history'),
]