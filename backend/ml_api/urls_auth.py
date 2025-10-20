from django.urls import path
from . import views_auth

app_name = 'auth'

urlpatterns = [
    # Rejestracja i logowanie
    path('register/', views_auth.register_user, name='register'),
    path('login/', views_auth.login_user, name='login'),
    path('logout/', views_auth.logout_user, name='logout'),
    
    # Profil użytkownika
    path('profile/', views_auth.user_profile, name='profile'),
    path('change-password/', views_auth.change_password, name='change_password'),
    
    # Status autoryzacji
    path('status/', views_auth.auth_status, name='status'),
    path('test/', views_auth.auth_test, name='test'),
]