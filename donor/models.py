from django.db import models
from django.contrib.auth.models import User

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
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"