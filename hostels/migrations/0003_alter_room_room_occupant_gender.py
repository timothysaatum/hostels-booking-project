# Generated by Django 4.1.7 on 2023-09-28 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hostels", "0002_hostel_description_roomtype_max_capacity_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="room_occupant_gender",
            field=models.CharField(blank=True, max_length=7),
        ),
    ]
