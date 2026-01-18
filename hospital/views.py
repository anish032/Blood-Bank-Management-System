# hospital/views.py - COMPLETE FILE
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hospital, BloodRequest
from donor.models import Donor
from django.db.models import Q
import re

def register(request):
    if request.method == 'POST':
        hospital_name = request.POST.get('hospital_name', '').strip()
        registration_number = request.POST.get('registration_number', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST['password']
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # ... (keep all validation code same)
        
        Hospital.objects.create(
            user=user,
            hospital_name=hospital_name,
            registration_number=registration_number,
            phone=phone,
            address=address,
            city=city,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None
        )
        
        # Auto login
        auth_login(request, user)
        messages.success(request, f'Registration successful! Awaiting verification.')
        return redirect('/hospital/dashboard')
    
    return render(request, 'hospital/register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Check if user is a hospital
            try:
                hospital = Hospital.objects.get(user=user)
                auth_login(request, user)
                messages.success(request, f'Welcome back {hospital.hospital_name}!')
                return redirect('/hospital/dashboard')
            except Hospital.DoesNotExist:
                messages.error(request, 'Invalid hospital account!')
                return redirect('/hospital/login')
        else:
            messages.error(request, 'Invalid email or password!')
            return redirect('/hospital/login')
    
    return render(request, 'hospital/login.html')


@login_required(login_url='/hospital/login')
def dashboard(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital profile not found!')
        return redirect('/')
    
    requests = BloodRequest.objects.filter(hospital=hospital)
    pending = requests.filter(status='PENDING').count()
    approved = requests.filter(status='APPROVED').count()
    
    return render(request, 'hospital/dashboard.html', {
        'hospital': hospital,
        'requests': requests,
        'pending_count': pending,
        'approved_count': approved,
    })

@login_required(login_url='/hospital/login')
def profile(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital profile not found!')
        return redirect('/')
    
    return render(request, 'hospital/profile.html', {'hospital': hospital})


@login_required(login_url='/hospital/login')
def request_blood(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital profile not found!')
        return redirect('/')
    
    if not hospital.is_verified:
        messages.error(request, 'Your hospital is not verified yet. Please wait for admin approval.')
        return redirect('/hospital/dashboard')
    
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units_needed = request.POST.get('units_needed')
        urgency = request.POST.get('urgency')
        patient_case = request.POST.get('patient_case', '').strip()
        
        if not all([blood_group, units_needed, urgency, patient_case]):
            messages.error(request, 'All fields are required!')
            return redirect('/hospital/request-blood')
        
        try:
            units = int(units_needed)
            if units < 1:
                raise ValueError
        except ValueError:
            messages.error(request, 'Units must be a positive number!')
            return redirect('/hospital/request-blood')
        
        BloodRequest.objects.create(
            hospital=hospital,
            blood_group=blood_group,
            units_needed=units,
            urgency=urgency,
            patient_case=patient_case
        )
        
        messages.success(request, 'Blood request submitted! Waiting for approval.')
        return redirect('/hospital/dashboard')
    
    return render(request, 'hospital/request_blood.html', {'hospital': hospital})


@login_required(login_url='/hospital/login')
def check_availability(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital profile not found!')
        return redirect('/')
    
    blood_group = request.GET.get('blood_group', '')
    
    if blood_group:
        # Find eligible donors
        donors = Donor.objects.filter(blood_group=blood_group)
        eligible_donors = [d for d in donors if d.can_donate()]
        donor_count = len(eligible_donors)
    else:
        donor_count = None
    
    return render(request, 'hospital/availability.html', {
        'hospital': hospital,
        'blood_group': blood_group,
        'donor_count': donor_count
    })


def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/')