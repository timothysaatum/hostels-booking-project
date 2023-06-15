# Generated by Django 4.1.7 on 2023-06-15 14:27

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


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
                ('contact', models.CharField(help_text='0589 693 6595', max_length=10)),
                ('display_image', models.ImageField(blank=True, default=None, upload_to='unarcom/hostel/images')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('no_of_rooms', models.PositiveIntegerField(help_text='E.g 20')),
                ('hostel_coordinates', models.CharField(help_text='latitude, longitude', max_length=100)),
                ('cost_range', models.CharField(help_text='4500', max_length=200)),
                ('duration_of_rent', models.PositiveIntegerField(help_text='2')),
                ('wifi', models.CharField(max_length=50)),
                ('hostel_amenities', models.JSONField(blank=True, default=dict, null=True)),
                ('account_number', models.CharField(blank=True, max_length=100, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_type', models.CharField(choices=[('1 in a room', '1 in a room'), ('2 in a room', '2 in a room'), ('3 in a room', '3 in a room'), ('4 in a room', '4 in a room')], max_length=20)),
                ('room_display_image', models.ImageField(blank=True, default=None, null=True, upload_to='unarcom/room_type/images')),
                ('room_type_number', models.PositiveIntegerField()),
                ('room_numbers', models.JSONField(default=dict)),
                ('room_capacity', models.PositiveIntegerField()),
                ('cost_per_head', models.DecimalField(decimal_places=2, max_digits=65)),
                ('db_use_only', models.PositiveIntegerField()),
                ('details', ckeditor_uploader.fields.RichTextUploadingField()),
                ('hostel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.hostel')),
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
            name='RoomTypeImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_type_images', models.ImageField(blank=True, default=None, upload_to='unarcom/room_type/images')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.roomtype')),
            ],
            options={
                'verbose_name_plural': 'Room Images',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField()),
                ('room_occupant_gender', models.CharField(default='M', max_length=10)),
                ('is_booked', models.BooleanField(default=False)),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.roomtype')),
            ],
        ),
        migrations.AddField(
            model_name='hostel',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostels.school'),
        ),
    ]
