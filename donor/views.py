from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Donor
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']
        blood_group = request.POST['blood_group']
        phone = request.POST['phone']
        address = request.POST['address']
        
        # Check if user exists
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('/donor/register')
        
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = full_name
        user.save()
        
        Donor.objects.create(user=user, blood_group=blood_group, phone=phone, address=address)
        messages.success(request, 'Registration successful!')
        return redirect('/admin')
    
    return render(request, 'donor/register.html')