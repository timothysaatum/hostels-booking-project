# Generated by Django 4.1.7 on 2023-06-10 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlass', '0004_booking_receit_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='receit_number',
            new_name='receipt_number',
        ),
    ]
