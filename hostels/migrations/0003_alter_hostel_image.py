# Generated by Django 4.1.7 on 2023-05-26 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0002_delete_hostelimages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostel',
            name='image',
            field=models.ImageField(blank=True, default=None, upload_to='unarcom/hostel/images'),
        ),
    ]