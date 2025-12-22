from django.contrib import admin
from .models import Donor, DonationHistory, Hospital, BloodRequest

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):

    list_display = ['user', 'blood_group', 'phone', 'last_donation_date', 'is_phone_verified']
    list_filter = ['blood_group', 'is_phone_verified']
    search_fields = ['user__first_name', 'user__last_name', 'phone']

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):

    list_display = ['donor', 'donation_date', 'blood_units', 'hospital']
    list_filter = ['donation_date', 'hospital']
    date_hierarchy = 'donation_date'

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'license_id']
    search_fields = ['name', 'license_id']

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'quantity_needed', 'hospital', 'required_date', 'status']
    list_filter = ['status', 'blood_group']
    list_editable = ['status']