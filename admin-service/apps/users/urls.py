from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListProxy.as_view(), name='user-list'),
    path('<str:pk>/', views.UserDetailProxy.as_view(), name='user-detail'),
]
