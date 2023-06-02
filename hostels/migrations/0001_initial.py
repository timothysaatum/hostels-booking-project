# Generated by Django 4.1.7 on 2023-06-02 05:45

import ckeditor_uploader.fields
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
            name='Hostel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(default='unarcom', help_text='Enter name of hostel owner', max_length=100)),
                ('campus', models.CharField(default='Main Campus', help_text='Enter campus the hostel is located', max_length=100)),
                ('hostel_name', models.CharField(default='unnamed hostel', max_length=50)),
                ('contact', phonenumber_field.modelfields.PhoneNumberField(help_text='+233 589 693 6595', max_length=128, region=None)),
                ('display_image', models.ImageField(blank=True, default=None, upload_to='unarcom/hostel/images')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('no_of_rooms', models.PositiveIntegerField(help_text='E.g 20')),
                ('hostel_coordinates', models.CharField(help_text='latitude, longitude', max_length=100)),
                ('cost_per_room', models.DecimalField(decimal_places=2, help_text='4500', max_digits=8)),
                ('duration_of_rent', models.PositiveIntegerField(help_text='2')),
                ('wifi', models.CharField(max_length=50)),
                ('hostel_amenities', models.JSONField(blank=True, default=dict, null=True)),
                ('details', ckeditor_uploader.fields.RichTextUploadingField(help_text='Enter anything that is not in the amenities')),
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
            name='HostelImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(blank=True, default=None, upload_to='unarcom/hostel/images')),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.hostel')),
            ],
        ),
        migrations.AddField(
            model_name='hostel',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.school'),
        ),
        migrations.AddField(
            model_name='hostel',
            name='user_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
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
