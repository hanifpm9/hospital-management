@echo off
cd C:\Users\hanif\Desktop\HospitalManagement\
call ..\env\Scripts\activate
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem