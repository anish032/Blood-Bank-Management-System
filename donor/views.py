
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Donor, DonationHistory, BloodRequest, Hospital
from django.contrib import messages
import re
from django.conf import settings
from twilio.rest import Client

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

        # Twilio Integration
        try:
            # Pull secrets from the .env file
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            twilio_phone_number = settings.TWILIO_PHONE_NUMBER
            client = Client(account_sid, auth_token)

            client.messages.create(
                body=f"Your Blood Bank verification code is: {donor.otp_code}",
                from_=twilio_phone_number,
                to=f"+977{donor.phone}"  # Ensures the Nepal country code is added
            )
            messages.success(request, 'Account created! An OTP has been sent to your phone.')
        except Exception as e:

            messages.warning(request, f"User created, but SMS could not be sent: {str(e)}")

            messages.info(request, f"DEBUG: Your test code is {donor.otp_code}")

        auth_login(request, user)
        return redirect('donor_profile')



        auth_login(request, user)
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


    can_donate_status = donor.can_donate()


    recent_requests = BloodRequest.objects.filter(requester=request.user).order_by('-created_at')[:5]


    recent_donations = DonationHistory.objects.filter(donor=donor).order_by('-donation_date')[:5]

    context = {
        'donor': donor,
        'can_donate': can_donate_status,
        'recent_requests': recent_requests,
        'recent_donations': recent_donations,
    }
    return render(request, 'donor/profile.html', context)

@login_required(login_url='/donor/login')
def history(request):
    donor = get_object_or_404(Donor, user=request.user)
    donations = donor.donations.all()
    return render(request, 'donor/history.html', {'donor': donor, 'donations': donations})


@login_required(login_url='/donor/login')
def request_blood(request):
    # Ensure donor profile exists
    donor, created = Donor.objects.get_or_create(user=request.user)

    # Only verified users can request blood
    if not donor.is_phone_verified:
        messages.warning(request, "Please verify your phone number before requesting blood.")
        return redirect('verify_otp')

    hospitals = Hospital.objects.all()

    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity')
        hospital_id = request.POST.get('hospital')
        required_date = request.POST.get('required_date')

        # Basic validation
        if not all([blood_group, quantity, hospital_id, required_date]):
            messages.error(request, "All fields are required.")
            return redirect('request_blood')

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


@login_required(login_url='/donor/login')
def resend_otp(request):
    donor = get_object_or_404(Donor, user=request.user)

    # 1. Generate a new code
    donor.generate_otp()

    # 2. Resend via Twilio using your settings configuration
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=f"Your new Blood Bank verification code is: {donor.otp_code}",
            from_=twilio_phone_number,
            to=f"+977{donor.phone}"
        )
        messages.success(request, 'A new OTP has been sent to your phone.')
    except Exception as e:
        messages.warning(request, f"SMS could not be sent: {str(e)}")
        # Fallback for testing
        messages.info(request, f"DEBUG: Your new test code is {donor.otp_code}")

    return redirect('verify_otp')