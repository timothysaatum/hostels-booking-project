# Generated by Django 5.0.3 on 2024-07-26 17:52

import ckeditor_uploader.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


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
                ('image', models.ImageField(default=None, upload_to='unarcom/apartment/images')),
                ('num_bedrooms', models.PositiveIntegerField()),
                ('num_bathrooms', models.PositiveIntegerField()),
                ('max_guests', models.PositiveIntegerField()),
                ('price_per_month', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(default=None, upload_to='unarcom/properties/images')),
                ('location', models.CharField(max_length=100)),
                ('property_type', models.CharField(max_length=200)),
                ('rating', models.PositiveIntegerField()),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
