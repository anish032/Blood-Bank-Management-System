from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Nepal mobile number validator: 10 digits, starts with 98, 97, or 96
nepal_phone_regex = RegexValidator(
    regex=r'^(98|97|96)\d{8}$',
    message="Enter a valid Nepali mobile number (98/97/96 followed by 8 digits)"
)

class Hospital(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)


    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    contact_number = models.CharField(
        max_length=10,
        validators=[nepal_phone_regex],
        unique=True
    )

    def __str__(self):
        return self.name
