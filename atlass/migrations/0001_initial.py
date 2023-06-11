# Generated by Django 4.1.7 on 2023-06-09 22:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hostels', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
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
                ('ref', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('is_verified', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.room')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.roomtype')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(default='GHS', max_length=50)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=65)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
