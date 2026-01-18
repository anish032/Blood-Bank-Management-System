from django.contrib import admin
from .models import Hospital, BloodRequest

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'city', 'phone', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'city']
    search_fields = ['hospital_name', 'registration_number']
    actions = ['verify_hospitals']
    
    def verify_hospitals(self, request, queryset):
        queryset.update(is_verified=True)
    verify_hospitals.short_description = "Verify selected hospitals"


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'blood_group', 'units_needed', 'urgency', 'status', 'requested_at']
    list_filter = ['status', 'urgency', 'blood_group']
    search_fields = ['hospital__hospital_name', 'patient_case']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_requests.short_description = "Reject selected requests"