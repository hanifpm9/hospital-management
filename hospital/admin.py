from django.contrib import admin
from .models import Doctor, Patient, Department, Appointment, Payment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'consultation_fee', 'license_number')  # Ensure these fields exist in the Doctor model

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('uhid', 'name', 'gender', 'phone_number', 'registration_fee_paid')  # Ensure these fields exist in the Patient model

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'token', 'consultation_fee')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'amount', 'payment_method', 'date')