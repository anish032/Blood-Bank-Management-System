from django.db import models
from django.contrib.auth.models import User

class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.hospital_name


class BloodRequest(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    URGENCY_LEVELS = [
        ('CRITICAL', 'Critical - Life Threatening'),
        ('URGENT', 'Urgent - Within 24 hours'),
        ('ROUTINE', 'Routine - Within a week'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='requests')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_needed = models.IntegerField()
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS)
    patient_case = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.blood_group} ({self.units_needed} units)"