from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', views.login, name='login'),
    path('auth/register/', views.register, name='register'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/refresh/', views.refresh_token, name='refresh_token'),
    path('auth/change-password/', views.change_password, name='change_password'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    
    # User preferences
    path('preferences/', views.user_preferences, name='user_preferences'),
    
    # Search history
    path('history/add/', views.add_to_search_history, name='add_history'),
    path('history/', views.get_search_history, name='get_history'),
    path('history/clear/', views.clear_search_history, name='clear_history'),
    
    # Password update
    path('password/update/', views.update_password, name='update_password'),
]
