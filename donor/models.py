from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date, timedelta
import random

# Validator for Nepali Phone Numbers
nepal_phone_regex = RegexValidator(
    regex=r'^9[78]\d{8}$',
    message="Phone number must be a valid 10-digit Nepali mobile number (starting with 98 or 97)."
)

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    license_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone = models.CharField(validators=[nepal_phone_regex], max_length=10, unique=True)
    address = models.TextField()
    last_donation_date = models.DateField(null=True, blank=True)


    is_phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"

    def can_donate(self):
        if not self.last_donation_date:
            return True
        days_since = (date.today() - self.last_donation_date).days
        return days_since >= 90

    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.save()
        return self.otp_code

class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'), ('Approved', 'Approved'),
        ('Fulfilled', 'Fulfilled'), ('Cancelled', 'Cancelled'),
    ]
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=Donor.BLOOD_GROUPS)
    quantity_needed = models.PositiveIntegerField(default=1)

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    required_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blood_group} request for {self.hospital.name}"

class DonationHistory(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateField(auto_now_add=True)
    blood_units = models.IntegerField(default=1)

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-donation_date']
        verbose_name_plural = "Donation Histories"

    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.donation_date}"