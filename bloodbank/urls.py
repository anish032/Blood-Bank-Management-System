from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('search-donors/', views.search_donors, name='search_donors'),
    path('map-donors/', views.map_donors, name='map_donors'),  # Add this
    path('donor/', include('donor.urls')),
    path('hospital/', include('hospital.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)