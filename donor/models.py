from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    last_donation_date = models.DateField(null=True, blank=True)
    
    # Verification fields
    verification_document = models.ImageField(upload_to='donor_documents/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    # Location fields
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, default='Biratnagar')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"
    
    def can_donate(self):
        """Check if donor is verified and eligible to donate"""
        if not self.is_verified:
            return False
        if not self.last_donation_date:
            return True
        days_since = (date.today() - self.last_donation_date).days
        return days_since >= 90
    
    def next_eligible_date(self):
        """Calculate next eligible donation date"""
        if not self.last_donation_date:
            return date.today()
        return self.last_donation_date + timedelta(days=90)


class DonationHistory(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateField(auto_now_add=True)
    blood_units = models.IntegerField(default=1)
    hospital_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-donation_date']
        verbose_name_plural = "Donation Histories"
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.donation_date}"