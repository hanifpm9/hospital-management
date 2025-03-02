# hospital/forms.py
from django import forms
from .models import Appointment, Patient, Doctor, Department

print("Loading forms.py")  # Debugging statement

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['title', 'name', 'gender', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'cols': 20}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'department', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'patient' in self.initial:
            patient = Patient.objects.get(id=self.initial['patient'])
            self.fields['patient'].initial = patient.id
            self.fields['patient'].widget.attrs['readonly'] = True  # Make the field read-only