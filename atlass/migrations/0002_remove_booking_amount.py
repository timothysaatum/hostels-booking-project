# Generated by Django 4.1.7 on 2023-06-04 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlass', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='amount',
        ),
    ]
