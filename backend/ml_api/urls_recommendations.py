from django.urls import path
from . import views_recommendations

app_name = 'recommendations'

urlpatterns = [
    path('collaborative/me/', views_recommendations.collaborative_recommendations, name='collaborative_me'),
    path('collaborative/<int:user_id>/', views_recommendations.collaborative_recommendations, name='collaborative_for_user'),
    path('collaborative/', views_recommendations.collaborative_recommendations, name='collaborative'),
]