# Generated by Django 4.1.7 on 2023-07-16 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostels', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostel',
            name='account_name',
            field=models.CharField(default='unarcom', max_length=100),
            preserve_default=False,
        ),
    ]