from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='donor_register'),
    path('login/', views.login, name='donor_login'),
    path('profile/', views.profile, name='donor_profile'),
    path('logout/', views.logout, name='donor_logout'),
    path('history/', views.history, name='donor_history'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
path('verify-otp/resend/', views.resend_otp, name='resend_otp'),
path('request-blood/', views.request_blood, name='request_blood'),


]