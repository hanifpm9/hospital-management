from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django default admin panel
    path('hospital/', include('hospital.urls')),  # Include hospital app URLs
]
