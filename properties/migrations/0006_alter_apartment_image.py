# Generated by Django 4.1.7 on 2023-05-29 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_property_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='image',
            field=models.ImageField(default=None, upload_to='unarcom/apartment/images'),
        ),
    ]