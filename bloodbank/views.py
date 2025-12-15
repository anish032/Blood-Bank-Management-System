from django.shortcuts import render
from donor.models import Donor
from django.db.models import Count

def home(request):
    total_donors = Donor.objects.count()
    return render(request, 'home.html', {'total_donors': total_donors})

def dashboard(request):
    total_donors = Donor.objects.count()
    blood_groups = Donor.objects.values('blood_group').annotate(count=Count('blood_group'))
    return render(request, 'dashboard.html', {
        'total_donors': total_donors,
        'blood_groups': blood_groups
    })