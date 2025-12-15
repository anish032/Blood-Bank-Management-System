from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='donor_register'),
    path('login/', views.login, name='donor_login'),
    path('profile/', views.profile, name='donor_profile'),
    path('logout/', views.logout, name='donor_logout'),
    path('history/', views.history, name='donor_history'),
]