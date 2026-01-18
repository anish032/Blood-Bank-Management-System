from django.shortcuts import render, redirect
from donor.models import Donor
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone

def home(request):
    # Smart redirect based on user type
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/manage-requests')
        else:
            # Check if hospital or donor
            from hospital.models import Hospital  # Import here to avoid circular import
            try:
                hospital = Hospital.objects.get(user=request.user)
                return redirect('/hospital/dashboard')
            except Hospital.DoesNotExist:
                try:
                    donor = Donor.objects.get(user=request.user)
                    return redirect('/donor/profile')
                except Donor.DoesNotExist:
                    pass
    
    # Not logged in - show public home page
    total_donors = Donor.objects.count()
    return render(request, 'home.html', {'total_donors': total_donors})

def dashboard(request):
    total_donors = Donor.objects.count()
    blood_groups = Donor.objects.values('blood_group').annotate(count=Count('blood_group'))
    return render(request, 'dashboard.html', {
        'total_donors': total_donors,
        'blood_groups': blood_groups
    })

@staff_member_required
def manage_requests(request):
    from hospital.models import BloodRequest  # Import here
    
    pending_requests = BloodRequest.objects.filter(status='PENDING').order_by('-requested_at')
    all_requests = BloodRequest.objects.all().order_by('-requested_at')[:20]
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        try:
            blood_request = BloodRequest.objects.get(id=request_id)
            
            if action == 'approve':
                blood_request.status = 'APPROVED'
                blood_request.approved_by = request.user
                blood_request.approved_at = timezone.now()
                blood_request.remarks = remarks
                blood_request.save()
                messages.success(request, f'Request from {blood_request.hospital.hospital_name} approved!')
            
            elif action == 'reject':
                blood_request.status = 'REJECTED'
                blood_request.approved_by = request.user
                blood_request.approved_at = timezone.now()
                blood_request.remarks = remarks
                blood_request.save()
                messages.warning(request, f'Request from {blood_request.hospital.hospital_name} rejected!')
            
            elif action == 'fulfill':
                blood_request.status = 'FULFILLED'
                blood_request.save()
                messages.success(request, 'Request marked as fulfilled!')
                
        except BloodRequest.DoesNotExist:
            messages.error(request, 'Request not found!')
        
        return redirect('/manage-requests')
    
    return render(request, 'manage_requests.html', {
        'pending_requests': pending_requests,
        'all_requests': all_requests
    })

@staff_member_required
def search_donors(request):
    blood_group = request.GET.get('blood_group', '')
    
    if blood_group:
        donors = Donor.objects.filter(blood_group=blood_group)
        eligible_donors = [d for d in donors if d.can_donate()]
    else:
        eligible_donors = []
    
    return render(request, 'search_donors.html', {
        'blood_group': blood_group,
        'donors': eligible_donors
    })

from math import radians, sin, cos, sqrt, atan2

@staff_member_required
def map_donors(request):
    blood_group = request.GET.get('blood_group', '')
    radius = int(request.GET.get('radius', 100))
    
    donors = []
    
    if blood_group:
        all_donors = Donor.objects.filter(blood_group=blood_group, is_verified=True)
        
        # Biratnagar coordinates (reference point)
        ref_lat = 26.4525
        ref_lon = 87.2718
        
        for donor in all_donors:
            if donor.can_donate():
                # Calculate distance if coordinates available
                if donor.latitude and donor.longitude:
                    distance = calculate_distance(ref_lat, ref_lon, 
                                                 float(donor.latitude), float(donor.longitude))
                    donor.distance = distance
                    
                    # Filter by radius
                    if distance <= radius:
                        donors.append(donor)
                else:
                    donor.distance = None
                    donors.append(donor)
        
        # Sort by distance
        donors.sort(key=lambda x: x.distance if x.distance else 999)
    
    return render(request, 'map_donors.html', {
        'donors': donors,
        'blood_group': blood_group,
        'radius': str(radius)
    })

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c