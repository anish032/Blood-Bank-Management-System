from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


nepal_phone_regex = RegexValidator(
    regex=r'^(98|97|96)\d{8}$',
    message="Enter a valid Nepali mobile number (98/97/96 followed by 8 digits)"
)

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)


    age = models.PositiveIntegerField(default=20)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone = models.CharField(
        max_length=10,
        validators=[nepal_phone_regex],
        unique=True
    )
    address = models.TextField()
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}"
