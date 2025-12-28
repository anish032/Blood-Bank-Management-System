from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Donor, DonationHistory
from django.contrib import messages
import re

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST['password']
        blood_group = request.POST['blood_group']
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        if not all([first_name, last_name, email, phone, address]):
            messages.error(request, 'All fields are required!')
            return redirect('/donor/register')
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, 'Invalid email format!')
            return redirect('/donor/register')
        
        if not re.match(r'^9\d{9}$', phone):
            messages.error(request, 'Phone must be 10 digits starting with 9!')
            return redirect('/donor/register')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('/donor/register')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        Donor.objects.create(user=user, blood_group=blood_group, phone=phone, address=address)
        
        # Auto login after registration
        auth_login(request, user)
        messages.success(request, 'Registration successful! Welcome!')
        return redirect('/donor/profile')
    
    return render(request, 'donor/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back {user.first_name}!')
            return redirect('/donor/profile')
        else:
            messages.error(request, 'Invalid email or password!')
            return redirect('/donor/login')
    
    return render(request, 'donor/login.html')

@login_required(login_url='/donor/login')
def profile(request):
    donor = Donor.objects.get(user=request.user)
    return render(request, 'donor/profile.html', {'donor': donor})

@login_required(login_url='/donor/login')
def history(request):
    donor = Donor.objects.get(user=request.user)
    donations = donor.donations.all()
    return render(request, 'donor/history.html', {'donor': donor, 'donations': donations})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/')

##################################################################################################
#mapapiadded
from django.http import JsonResponse
from .models import Donor
from .utils import calculate_distance

def donor_map_data(request):
    blood_group = request.GET.get('blood_group')
    max_distance = float(request.GET.get('distance', 10))

    user_lat = float(request.GET.get('lat'))
    user_lng = float(request.GET.get('lng'))

    donors = Donor.objects.filter(is_available=True)

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    result = []

    for donor in donors:
        if donor.latitude and donor.longitude:
            distance = calculate_distance(
                user_lat, user_lng,
                donor.latitude, donor.longitude
            )

            if distance <= max_distance:
                result.append({
                    'name': donor.user.get_full_name(),
                    'blood_group': donor.blood_group,
                    'lat': donor.latitude,
                    'lng': donor.longitude,
                    'distance': round(distance, 2),
                })

    return JsonResponse({'donors': result})

def donor_map_page(request):
    return render(request, 'donor/map.html')

