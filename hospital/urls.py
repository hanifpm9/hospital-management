from django.urls import path
from . import views

urlpatterns = [
    # Appointment-related URLs
    path('appointment/', views.appointment_form, name='appointment_form'),  # Without patient_id
    path('appointment/<int:patient_id>/', views.appointment_form, name='appointment_form_with_id'),  # With patient_id

    # Payment-related URLs
    path('payment/<int:appointment_id>/', views.payment_page, name='payment_page'),
    path('payment/<int:appointment_id>/print/', views.print_receipt, name='print_receipt'),

    # Other URLs
    path('register/', views.register_patient, name='register_patient'),
    path('appointment-list/', views.appointment_list, name='appointment_list'),
    path('payment-details/', views.payment_details, name='payment_details'),
    path('patient-list/', views.patient_list, name='patient_list'),
    path('revenue-report/', views.revenue_report, name='revenue_report'),
    path('search-patient/', views.search_patient, name='search_patient'),
    path('', views.home, name='home'),  # Home page
]