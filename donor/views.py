# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# from django.contrib.auth.decorators import login_required
# from .models import Donor, DonationHistory
# from django.contrib import messages
# import re
#
# def register(request):
#     if request.method == 'POST':
#         first_name = request.POST.get('first_name', '').strip()
#         last_name = request.POST.get('last_name', '').strip()
#         email = request.POST.get('email', '').strip()
#         password = request.POST['password']
#         blood_group = request.POST['blood_group']
#         phone = request.POST.get('phone', '').strip()
#         address = request.POST.get('address', '').strip()
#
#         if not all([first_name, last_name, email, phone, address]):
#             messages.error(request, 'All fields are required!')
#             return redirect('/donor/register')
#
#         if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
#             messages.error(request, 'Invalid email format!')
#             return redirect('/donor/register')
#
#         if not re.match(r'^9\d{9}$', phone):
#             messages.error(request, 'Phone must be 10 digits starting with 9!')
#             return redirect('/donor/register')
#
#         if User.objects.filter(username=email).exists():
#             messages.error(request, 'Email already registered!')
#             return redirect('/donor/register')
#
#         user = User.objects.create_user(username=email, email=email, password=password)
#         user.first_name = first_name
#         user.last_name = last_name
#         user.save()
#
#         Donor.objects.create(user=user, blood_group=blood_group, phone=phone, address=address)
#
#         # Auto login after registration
#         auth_login(request, user)
#         messages.success(request, 'Registration successful! Welcome!')
#         return redirect('/donor/profile')
#
#     return render(request, 'donor/register.html')
#
# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             auth_login(request, user)
#             messages.success(request, f'Welcome back {user.first_name}!')
#             return redirect('/donor/profile')
#         else:
#             messages.error(request, 'Invalid email or password!')
#             return redirect('/donor/login')
#
#     return render(request, 'donor/login.html')
#
# @login_required(login_url='/donor/login')
# def profile(request):
#     donor = Donor.objects.get(user=request.user)
#     return render(request, 'donor/profile.html', {'donor': donor})
#
# @login_required(login_url='/donor/login')
# def history(request):
#     donor = Donor.objects.get(user=request.user)
#     donations = donor.donations.all()
#     return render(request, 'donor/history.html', {'donor': donor, 'donations': donations})
#
# def logout(request):
#     auth_logout(request)
#     messages.success(request, 'Logged out successfully!')
#     return redirect('/')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Donor, DonationHistory, BloodRequest, Hospital
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
            return redirect('donor_register')

        # Matches Nepali Phone Format (starts with 97 or 98)
        if not re.match(r'^9[78]\d{8}$', phone):
            messages.error(request, 'Phone must be 10 digits starting with 98 or 97!')
            return redirect('donor_register')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('donor_register')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        donor = Donor.objects.create(user=user, blood_group=blood_group, phone=phone, address=address)
        donor.generate_otp()

        auth_login(request, user)
        # Showing the OTP in a message so you can test without an SMS gateway
        messages.success(request, f'Account created! Your verification code is: {donor.otp_code}')
        return redirect('donor_profile')

    return render(request, 'donor/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back {user.first_name}!')
            return redirect('donor_profile')
        else:
            messages.error(request, 'Invalid email or password!')
            return redirect('donor_login')

    return render(request, 'donor/login.html')

@login_required(login_url='/donor/login')
def profile(request):
    donor = get_object_or_404(Donor, user=request.user)
    return render(request, 'donor/profile.html', {'donor': donor})

@login_required(login_url='/donor/login')
def history(request):
    donor = get_object_or_404(Donor, user=request.user)
    donations = donor.donations.all()
    return render(request, 'donor/history.html', {'donor': donor, 'donations': donations})

@login_required(login_url='/donor/login')
def request_blood(request):
    hospitals = Hospital.objects.all()
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity')
        hospital_id = request.POST.get('hospital')
        required_date = request.POST.get('required_date')

        hospital = get_object_or_404(Hospital, id=hospital_id)

        BloodRequest.objects.create(
            requester=request.user,
            blood_group=blood_group,
            quantity_needed=quantity,
            hospital=hospital,
            required_date=required_date
        )
        messages.success(request, 'Blood request submitted successfully!')
        return redirect('donor_profile')

    return render(request, 'donor/request_blood.html', {'hospitals': hospitals})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('/')


@login_required(login_url='/donor/login')
def verify_otp(request):
    donor = get_object_or_404(Donor, user=request.user)

    if request.method == 'POST':
        user_otp = request.POST.get('otp_code')

        if donor.otp_code == user_otp:
            donor.is_phone_verified = True
            donor.otp_code = None  # Clear the OTP after successful verification
            donor.save()
            messages.success(request, 'Phone number verified successfully!')
            return redirect('donor_profile')
        else:
            messages.error(request, 'Invalid OTP code. Please try again.')

    return render(request, 'donor/verify_otp.html')