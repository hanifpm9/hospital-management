# Generated by Django 5.1.5 on 2025-02-20 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_appointment_next_appointment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='registration_fee_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='consultation_fee',
            field=models.DecimalField(decimal_places=2, default=200.0, max_digits=10),
        ),
    ]
