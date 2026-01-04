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
from .models import Donor, DonationHistory, BloodRequest, Hospital, Notification
from django.contrib import messages
import re
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
import math
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import os

@ensure_csrf_cookie
def donor_map_page(request):
    return render(request, 'donor/map.html', {'user_is_authenticated': request.user.is_authenticated})


def resendOtp(request):
    return JsonResponse({"status": "ok", "message": "OTP resent successfully"})

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

        # Prevent duplicate phone numbers
        if Donor.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered!')
            return redirect('donor_register')

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        try:
            donor = Donor.objects.create(user=user, blood_group=blood_group, phone=phone, address=address)
        except IntegrityError:
            messages.error(request, 'Phone number already registered!')
            user.delete()
            return redirect('donor_register')
        donor.generate_otp()

        auth_login(request, user)
        # Showing the OTP in a message so you can test without an SMS gateway
        messages.success(request, f'Account created! Your verification code is: {donor.otp_code}')
        return redirect('donor_profile')

    return render(request, 'donor/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Try authenticating directly with provided email (stored as username),
        # otherwise try to resolve user by email and authenticate with their username.
        user = authenticate(request, username=email, password=password)
        if user is None:
            try:
                candidate = User.objects.filter(email__iexact=email).first()
                if candidate:
                    user = authenticate(request, username=candidate.username, password=password)
            except Exception:
                user = None
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
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.info(request, 'Please complete your donor registration to access your profile.')
        return redirect('donor_complete_registration')
    return render(request, 'donor/profile.html', {'donor': donor})

@login_required(login_url='/donor/login')
def history(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.info(request, 'Please complete your donor registration to view donation history.')
        return redirect('donor_register')
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

        br = BloodRequest.objects.create(
            requester=request.user,
            blood_group=blood_group,
            quantity_needed=quantity,
            hospital=hospital,
            required_date=required_date
        )
        # Notification for requester
        Notification.objects.create(user=request.user, verb='Blood request submitted', data={'request_id': br.id, 'blood_group': blood_group})
        # Notify staff/admins
        for admin_user in User.objects.filter(is_staff=True):
            Notification.objects.create(user=admin_user, verb=f'New blood request: {blood_group}', data={'request_id': br.id, 'requester': request.user.username})
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
            donor.otp_code = None
            donor.save()
            messages.success(request, 'Phone number verified successfully!')
            return redirect('donor_profile')
        else:
            messages.error(request, 'Invalid OTP code. Please try again.')

    return render(request, 'donor/verify_otp.html')
def donor_map_data(request):
    # Build list of entities (donors + hospitals) with coordinates
    data = []
    # Allow search query to filter donors by name or address
    q = request.GET.get('q', '').strip()
    donors_qs = Donor.objects.all()
    if q:
        donors_qs = donors_qs.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(address__icontains=q))
    for d in donors_qs:
        lat = getattr(d, 'latitude', None) or getattr(d, 'lat', None)
        lng = getattr(d, 'longitude', None) or getattr(d, 'lng', None) or getattr(d, 'long', None)
        if lat is None or lng is None:
            continue
        name = d.user.get_full_name() if hasattr(d, 'user') else str(d)
        data.append({
            'type': 'donor',
            'name': name,
            'blood_group': getattr(d, 'blood_group', ''),
            'blood_type_verified': getattr(d, 'blood_type_verified', False),
            'lat': lat,
            'lng': lng,
        })

    # include hospitals (if coordinates exist)
    hospitals_qs = Hospital.objects.all()
    for h in hospitals_qs:
        lat = getattr(h, 'latitude', None) or getattr(h, 'lat', None)
        lng = getattr(h, 'longitude', None) or getattr(h, 'lng', None) or getattr(h, 'long', None)
        if lat is None or lng is None:
            continue
        data.append({
            'type': 'hospital',
            'name': h.name,
            'hospital_id': h.id,
            'lat': lat,
            'lng': lng,
        })
    # Optional filtering by blood group and distance (km)
    try:
        q_lat = request.GET.get('lat')
        q_lng = request.GET.get('lng')
        blood_group = request.GET.get('blood_group')
        distance_km = float(request.GET.get('distance', 0)) if request.GET.get('distance') else None
        if q_lat and q_lng and distance_km:
            q_lat = float(q_lat); q_lng = float(q_lng)
            def haversine(lat1, lon1, lat2, lon2):
                # returns distance in km
                R = 6371.0
                phi1 = math.radians(lat1)
                phi2 = math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlambda = math.radians(lon2 - lon1)
                a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            filtered = []
            for item in data:
                # If blood_group filter is provided, apply it only to donors
                if blood_group and blood_group != '' and item.get('type') == 'donor' and item.get('blood_group') != blood_group:
                    continue
                d_km = haversine(q_lat, q_lng, item['lat'], item['lng'])
                if d_km <= distance_km:
                    item['distance'] = round(d_km, 2)
                    filtered.append(item)
            return JsonResponse({'donors': filtered})
    except Exception:
        pass

    # Also include recent blood requests (use hospital coords)
    requests_qs = BloodRequest.objects.filter(status='Pending')[:100]
    for r in requests_qs:
        h = r.hospital
        if getattr(h, 'latitude', None) is None or getattr(h, 'longitude', None) is None:
            continue
        data.append({
            'type': 'request',
            'name': f'Request: {r.blood_group} x{r.quantity_needed}',
            'blood_group': r.blood_group,
            'quantity_needed': r.quantity_needed,
            'lat': h.latitude,
            'lng': h.longitude,
            'request_id': r.id,
            'required_date': str(r.required_date),
        })

    # Apply only_verified filter if requested (client-side may send only_verified=1)
    only_verified = request.GET.get('only_verified')
    if only_verified in ('1', 'true', 'True'):
        filtered = [item for item in data if not (item.get('type') == 'donor' and not item.get('blood_type_verified'))]
        return JsonResponse({'donors': filtered})

    # Support search returning filtered list (if 'q' present we already filtered donors_qs)

    return JsonResponse({'donors': data})


@require_POST
@login_required
def add_location(request):
    # Accept JSON or form data: lat, lng
    lat = request.POST.get('lat') or (request.body and None)
    lng = request.POST.get('lng') or (request.body and None)
    # If JSON body
    if request.content_type == 'application/json':
        import json
        try:
            payload = json.loads(request.body.decode())
            lat = payload.get('lat')
            lng = payload.get('lng')
        except Exception:
            pass

    if not lat or not lng:
        return JsonResponse({'status': 'error', 'message': 'Missing lat/lng'}, status=400)

    try:
        donor = Donor.objects.get(user=request.user)
        donor.latitude = float(lat)
        donor.longitude = float(lng)
        donor.save()
        # Notify user that location was saved
        Notification.objects.create(user=request.user, verb='Location updated', data={'lat': donor.latitude, 'lng': donor.longitude})
        return JsonResponse({'status': 'ok'})
    except Donor.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Donor profile not found'}, status=404)


@login_required(login_url='/donor/login')
def complete_registration(request):
    # Allows a logged-in user to complete donor info if Donor record is missing
    try:
        existing = Donor.objects.get(user=request.user)
        return redirect('donor_profile')
    except Donor.DoesNotExist:
        pass

    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        id_file = request.FILES.get('id_document')

        if not all([blood_group, phone, address]):
            messages.error(request, 'All fields are required')
            return redirect('donor_complete_registration')

        # Validate Nepali phone
        if not re.match(r'^9[78]\d{8}$', phone):
            messages.error(request, 'Phone must be 10 digits starting with 98 or 97!')
            return redirect('donor_complete_registration')

        if Donor.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered')
            return redirect('donor_complete_registration')

        donor = Donor.objects.create(user=request.user, blood_group=blood_group, phone=phone, address=address)
        if id_file:
            donor.id_document.save(id_file.name, id_file, save=True)
        messages.success(request, 'Donor profile created successfully')
        return redirect('donor_profile')

    # Render a simple completion form
    return render(request, 'donor/complete_registration.html', {'user': request.user, 'blood_groups': Donor.BLOOD_GROUPS})


@login_required(login_url='/donor/login')
@require_http_methods(['GET', 'POST'])
def upload_id_document(request):
    try:
        donor = Donor.objects.get(user=request.user)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found. Please complete registration first.')
        return redirect('donor_complete_registration')

    if request.method == 'POST':
        f = request.FILES.get('id_document')
        if not f:
            messages.error(request, 'Please select a file to upload.')
            return redirect('donor_profile')
        # Save file to donor.id_document
        donor.id_document.save(f.name, f, save=True)
        messages.success(request, 'ID document uploaded. An admin will verify your blood group shortly.')
        # Notify user and admins
        Notification.objects.create(user=request.user, verb='ID document uploaded', data={'file': donor.id_document.name})
        for admin_user in User.objects.filter(is_staff=True):
            Notification.objects.create(user=admin_user, verb=f'ID uploaded for {request.user.username}', data={'donor_id': donor.id})
        return redirect('donor_profile')

    return render(request, 'donor/upload_id.html', {'donor': donor})


@login_required
def notifications_api(request):
    # Return unread count and recent notifications for the logged-in user
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    items = []
    for n in notifs:
        items.append({'id': n.id, 'verb': n.verb, 'data': n.data or {}, 'is_read': n.is_read, 'created_at': n.created_at.isoformat()})
    return JsonResponse({'unread_count': unread, 'notifications': items})


@require_POST
@login_required
def mark_notification_read(request):
    nid = request.POST.get('id')
    if nid == 'all':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})
    try:
        n = Notification.objects.get(id=int(nid), user=request.user)
        n.is_read = True
        n.save()
        return JsonResponse({'status': 'ok'})
    except Exception:
        return JsonResponse({'status': 'error'}, status=400)
