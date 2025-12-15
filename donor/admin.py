from django.contrib import admin
from .models import Donor, DonationHistory

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'phone', 'last_donation_date', 'can_donate']
    list_filter = ['blood_group']
    search_fields = ['user__first_name', 'user__last_name', 'phone']

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'blood_units', 'hospital_name']
    list_filter = ['donation_date']
    date_hierarchy = 'donation_date'