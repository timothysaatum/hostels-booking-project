# Generated by Django 4.1.7 on 2023-05-26 06:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HostelImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files', models.ImageField(blank=True, default=None, upload_to='static/images')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('school_coordinates', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Hostel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(default='unarcom', max_length=100)),
                ('campus', models.CharField(default='Main Campus', max_length=100)),
                ('hostel_name', models.CharField(default='unnamed hostel', max_length=50)),
                ('contact', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('image', models.ImageField(blank=True, default=None, upload_to='static/images')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('no_of_rooms', models.PositiveIntegerField()),
                ('hostel_coordinates', models.CharField(max_length=100)),
                ('cost_per_room', models.DecimalField(decimal_places=2, max_digits=8)),
                ('duration', models.PositiveIntegerField()),
                ('wifi', models.CharField(blank=True, max_length=20, null=True)),
                ('toilet', models.CharField(blank=True, max_length=100, null=True)),
                ('study_area', models.CharField(blank=True, max_length=100, null=True)),
                ('water', models.CharField(blank=True, max_length=100, null=True)),
                ('bath_rooms', models.CharField(blank=True, max_length=200, null=True)),
                ('ac_fan', models.CharField(blank=True, max_length=100, null=True, verbose_name='AC/Fun')),
                ('power_supply', models.CharField(blank=True, max_length=200, null=True)),
                ('details', models.TextField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.school')),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateTimeField(default=django.utils.timezone.now)),
                ('phone_number', models.CharField(blank=True, max_length=10, null=True)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('room_no', models.PositiveIntegerField()),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email_address', models.EmailField(max_length=254)),
                ('city_or_town', models.CharField(max_length=100)),
                ('university_identification_number', models.PositiveIntegerField()),
                ('region_of_residence', models.CharField(max_length=100)),
                ('digital_address', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.hostel')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
