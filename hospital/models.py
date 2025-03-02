# hospital/models.py
from django.db import models
from django.utils import timezone

class Patient(models.Model):
    TITLE_CHOICES = [
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Master', 'Master'),
        ('Baby', 'Baby'),
        ('Baby of', 'Baby of'),
        ('Dr', 'Dr'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    uhid = models.CharField(max_length=20, unique=True, blank=True, null=True)
    registration_fee_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.uhid:  # Generate UHID if it doesn't exist
            last_patient = Patient.objects.order_by('-id').first()
            last_id = last_patient.id if last_patient else 0
            self.uhid = f"THQ{str(last_id + 1).zfill(5)}"  # Example: THQ00001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} {self.name} (UHID: {self.uhid})"

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    license_number = models.CharField(max_length=50, blank=True, null=True)  # Add this field if missing
    follow_up_days = models.IntegerField(default=14)  # Default follow-up period in days


    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Credit', 'Credit'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    appointment_time = models.DateTimeField(auto_now_add=True)
    token = models.IntegerField(default=1)  # Ensure token is not NULL
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, default='Pending')
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODES)
    next_appointment_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.token:
            last_appointment = Appointment.objects.filter(doctor=self.doctor, date=self.date).order_by('-token').first()
            if last_appointment and last_appointment.token is not None:
                self.token = last_appointment.token + 1
            else:
                self.token = 1  # Start from 1 if no appointments exist or token is NULL
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} ({self.date})"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Credit', 'Credit')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} by {self.patient.name} via {self.payment_method}"