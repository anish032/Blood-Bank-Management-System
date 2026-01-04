from django.contrib import admin
from .models import Donor, DonationHistory, Hospital, BloodRequest
from .models import Notification

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):

    list_display = ['user', 'blood_group', 'phone', 'last_donation_date', 'is_phone_verified', 'blood_type_verified']
    list_filter = ['blood_group', 'is_phone_verified']
    search_fields = ['user__first_name', 'user__last_name', 'phone']

    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        queryset.update(blood_type_verified=True)
    mark_verified.short_description = 'Mark selected donors as blood-type verified'

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):

    list_display = ['donor', 'donation_date', 'blood_units', 'hospital']
    list_filter = ['donation_date', 'hospital']
    date_hierarchy = 'donation_date'

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'license_id', 'latitude', 'longitude']
    search_fields = ['name', 'license_id']

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'quantity_needed', 'hospital', 'required_date', 'status']
    list_filter = ['status', 'blood_group']
    list_editable = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'verb', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'verb']