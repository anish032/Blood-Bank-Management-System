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
    path('verify-otp/resend/', views.resendOtp, name='resend_otp'),
    path('request-blood/', views.request_blood, name='donor_request_blood'),

    # MAP PAGE + API
    path('find-blood/', views.donor_map_page, name='find_blood'),
    path('map-data/', views.donor_map_data, name='donor_map_data'),
    path('add-location/', views.add_location, name='add_location'),
    path('complete-registration/', views.complete_registration, name='donor_complete_registration'),
    path('upload-id/', views.upload_id_document, name='upload_id_document'),
    # Notifications
    path('notifications/api/', views.notifications_api, name='notifications_api'),
    path('notifications/mark-read/', views.mark_notification_read, name='notifications_mark_read'),
]   