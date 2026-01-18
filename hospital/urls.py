from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='hospital_register'),
    path('login/', views.login, name='hospital_login'),
    path('dashboard/', views.dashboard, name='hospital_dashboard'),
    path('profile/', views.profile, name='hospital_profile'),  # Add this
    path('request-blood/', views.request_blood, name='request_blood'),
    path('availability/', views.check_availability, name='check_availability'),
    path('logout/', views.logout, name='hospital_logout'),
]