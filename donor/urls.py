from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='donor_register'),
    path('login/', views.login, name='donor_login'),
    path('profile/', views.profile, name='donor_profile'),
    path('logout/', views.logout, name='donor_logout'),
    path('history/', views.history, name='donor_history'),

    # OTP
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # MAP PAGE + API
    path('find-blood/', views.donor_map_page, name='find-blood'),
    path('map-data/', views.donor_map_data, name='donor-map-data'),
]
