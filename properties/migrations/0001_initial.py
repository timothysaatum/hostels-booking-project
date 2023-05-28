# Generated by Django 4.1.7 on 2023-05-26 06:02

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
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact', models.CharField(max_length=10)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('city', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=255)),
                ('image', models.ImageField(default=None, upload_to='static/apartment_images')),
                ('num_bedrooms', models.IntegerField()),
                ('num_bathrooms', models.IntegerField()),
                ('max_guests', models.IntegerField()),
                ('price_per_month', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('property_type', models.CharField(max_length=200)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
