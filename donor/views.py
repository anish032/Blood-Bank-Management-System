# MAP FEATURE
from django.http import JsonResponse
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

# OTP FEATURE
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
