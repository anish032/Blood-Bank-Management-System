from django.contrib import admin
from .models import Donor, DonationHistory
from django.utils.html import format_html

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'phone', 'is_verified', 'last_donation_date', 'can_donate']
    list_filter = ['is_verified', 'blood_group']
    search_fields = ['user__first_name', 'user__last_name', 'phone']
    actions = ['verify_donors', 'unverify_donors']
    readonly_fields = ['verification_image_preview']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'blood_group', 'phone', 'address')
        }),
        ('Verification', {
            'fields': ('verification_document', 'verification_image_preview', 'is_verified', 'verification_notes')
        }),
        ('Donation Info', {
            'fields': ('last_donation_date',)
        }),
    )
    
    def verification_image_preview(self, obj):
        if obj.verification_document:
            return format_html('<img src="{}" width="300" />', obj.verification_document.url)
        return "No document uploaded"
    verification_image_preview.short_description = "Document Preview"
    
    def verify_donors(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} donor(s) verified successfully!")
    verify_donors.short_description = "✓ Verify selected donors"
    
    def unverify_donors(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} donor(s) unverified!")
    unverify_donors.short_description = "✗ Unverify selected donors"


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'blood_units', 'hospital_name']
    list_filter = ['donation_date']
    date_hierarchy = 'donation_date'