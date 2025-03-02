# hospital/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Patient, Appointment, Doctor, Department, Payment
from .forms import PatientRegistrationForm, AppointmentForm  # Ensure this import is correct
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registration_fee_paid = True
            patient.save()

            # Debug: Print patient details
            print(f"Patient saved: {patient.name}, UHID: {patient.uhid}, ID: {patient.id}")

            # Create a payment record for the registration fee
            Payment.objects.create(
                patient=patient,
                amount=30,  # Fixed registration fee
                payment_method='Cash',  # Default payment method
            )

            # Include UHID in the success message
            messages.success(request, f'Patient {patient.name} registered successfully with UHID: {patient.uhid}')

            # Debug: Print redirect URL
            print(f"Redirecting to: appointment_form_with_id with patient_id={patient.id}")

            return redirect('appointment_form_with_id', patient_id=patient.id)  # Redirect to appointment form
            print(f"Redirect URL: {redirect_url}")
            return redirect(redirect_url)
        else:
            # Debug: Print form errors
            print(form.errors)
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})

def appointment_form(request, patient_id=None):
    patients = Patient.objects.all()
    departments = Department.objects.all()

    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
        initial_data = {'patient': patient.id}  # Pre-populate the patient field
        form = AppointmentForm(initial=initial_data)
    else:
        form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)

            # Fetch the selected patient and doctor
            patient_id = request.POST.get('patient')
            doctor_id = request.POST.get('doctor')
            date = request.POST.get('date')

            # Validate patient_id and doctor_id
            if not patient_id or not doctor_id:
                return render(request, 'appointment_form.html', {
                    'form': form,
                    'patients': patients,
                    'departments': departments,
                    'error': 'Please select a patient and a doctor.',
                })

            try:
                patient = Patient.objects.get(id=int(patient_id))
                doctor = Doctor.objects.get(id=int(doctor_id))
            except (Patient.DoesNotExist, Doctor.DoesNotExist, ValueError):
                return render(request, 'appointment_form.html', {
                    'form': form,
                    'patients': patients,
                    'departments': departments,
                    'error': 'Invalid patient or doctor selected.',
                })

            # Check for duplicate appointment
            if Appointment.objects.filter(patient=patient, doctor=doctor, date=date).exists():
                return render(request, 'appointment_form.html', {
                    'form': form,
                    'patients': patients,
                    'departments': departments,
                    'error': 'This patient already has an appointment with the same doctor on this date.',
                })

            appointment.patient = patient
            appointment.doctor = doctor

            # Calculate the token number
            today = timezone.now().date()
            last_appointment = Appointment.objects.filter(
                doctor=doctor,
                date=today
            ).order_by('-token').first()

            if last_appointment:
                appointment.token = last_appointment.token + 1
            else:
                appointment.token = 1

            # Check if the patient has a paid appointment with the same doctor within the follow-up days
            follow_up_days = doctor.follow_up_days  # Fetch follow-up days from the doctor's profile
            last_paid_appointment = Appointment.objects.filter(
                patient=patient,
                doctor=doctor,
                amount_paid__gt=0,  # Ensure the appointment was paid
                date__gte=appointment.date - timedelta(days=follow_up_days)  # Within the follow-up days
            ).first()

            if last_paid_appointment:
                # Follow-up appointment: No consultation fee
                appointment.consultation_fee = 0.00
            else:
                # New appointment: Fetch consultation fee from the doctor
                appointment.consultation_fee = doctor.consultation_fee

            appointment.save()

            # Create a payment record for the consultation fee (if applicable)
            if appointment.consultation_fee > 0:
                Payment.objects.create(
                    patient=patient,
                    amount=appointment.consultation_fee,
                    payment_method='Cash',  # Default payment method
                )

            return redirect('payment_page', appointment_id=appointment.id)
    else:
        form = AppointmentForm()

    return render(request, 'appointment_form.html', {
        'form': form,
        'patients': patients,
        'departments': departments,
    })

def appointment_page(request):
    appointments = Appointment.objects.all()
    return render(request, 'appointment.html', {'appointments': appointments})

from decimal import Decimal

from django.contrib import messages
from decimal import Decimal

from decimal import Decimal

def payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    total_amount = appointment.consultation_fee + 30  # Add registration fee

    if request.method == 'POST':
        amount_received_str = request.POST.get('amount_received')
        payment_method = request.POST.get('payment_method')

        # Debug: Print form data
        print(f"Amount received: {amount_received_str}, Payment Method: {payment_method}")

        if not amount_received_str:
            messages.error(request, 'Amount received is required.')
            return render(request, 'payment_page.html', {'appointment': appointment})

        try:
            amount_received = Decimal(amount_received_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount received. Please enter a valid number.')
            return render(request, 'payment_page.html', {'appointment': appointment})

        # Check if the amount received is sufficient
        if amount_received < total_amount:
            messages.error(request, f'Amount received (₹{amount_received}) is less than the total amount due (₹{total_amount}).')
            return render(request, 'payment_page.html', {'appointment': appointment})

        # Create payment record
        Payment.objects.create(
            patient=appointment.patient,
            amount=amount_received,
            payment_method=payment_method,
        )

        balance = amount_received - total_amount
        messages.success(request, f'Payment successful! Received: ₹{amount_received} | Balance: ₹{balance}')
        return redirect('print_receipt', appointment_id=appointment.id)

    return render(request, 'payment_page.html', {'appointment': appointment})

def payment_details(request, patient_id=None):
    payments = Payment.objects.all().order_by('-date')
    paginator = Paginator(payments, 50)  # Show 50 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'payment_list.html', {'page_obj': page_obj})

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Appointment, Payment

def payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    total_amount = appointment.consultation_fee + 30  # Add registration fee

    if request.method == 'POST':
        amount_received_str = request.POST.get('amount_received')
        payment_method = request.POST.get('payment_method')

        # Debug: Print form data
        print(f"Amount received: {amount_received_str}, Payment Method: {payment_method}")

        if not amount_received_str:
            messages.error(request, 'Amount received is required.')
            return render(request, 'payment_page.html', {'appointment': appointment})

        try:
            amount_received = Decimal(amount_received_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount received. Please enter a valid number.')
            return render(request, 'payment_page.html', {'appointment': appointment})

        if amount_received < total_amount:
            messages.error(request, 'Amount received is less than the total amount.')
            return render(request, 'payment_page.html', {'appointment': appointment})

        # Create payment record
        Payment.objects.create(
            patient=appointment.patient,
            amount=total_amount,
            payment_method=payment_method,
        )

        balance = amount_received - total_amount
        messages.success(request, f'Payment successful! Received: ₹{amount_received} | Balance: ₹{balance}')
        return redirect('print_receipt', appointment_id=appointment.id)

    return render(request, 'payment_page.html', {'appointment': appointment})

def appointment_list(request):
    date = request.GET.get('date', timezone.now().date())
    appointments = Appointment.objects.filter(date=date)
    return render(request, 'appointment_list.html', {'appointments': appointments})

def home(request):
    return render(request, 'home.html')

def patient_list(request):
    patients = Patient.objects.all()  # Fetch all patients
    return render(request, 'patient_list.html', {'patients': patients})

def revenue_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payments = Payment.objects.filter(date__range=[start_date, end_date])
    return render(request, 'revenue_report.html', {'payments': payments})

from django.http import JsonResponse
from .models import Patient
import logging
logger = logging.getLogger(__name__)

def search_patient(request):
    query = request.GET.get('query', '')
    patients = Patient.objects.filter(
        Q(name__icontains=query) | Q(uhid__icontains=query)
    )
    patient_list = [{'id': patient.id, 'name': patient.name, 'uhid': patient.uhid} for patient in patients]
    return JsonResponse({'patients': patient_list})

def print_receipt(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'print_receipt.html', {'appointment': appointment})

from django.http import JsonResponse

def get_doctors(request):
    department_id = request.GET.get('department_id')
    doctors = Doctor.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse({'doctors': list(doctors)})

def payment_list(request):
    payments = Payment.objects.all().order_by('-date')
    paginator = Paginator(payments, 50)  # Show 50 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'payment_list.html', {'page_obj': page_obj})

from django.core.paginator import Paginator

def patient_list(request):
    patients = Patient.objects.all()
    paginator = Paginator(patients, 10)  # Show 10 patients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'patient_list.html', {'page_obj': page_obj})
