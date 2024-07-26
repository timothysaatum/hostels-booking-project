# Generated by Django 4.1.7 on 2023-09-18 22:06

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hostels", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hostel",
            name="description",
            field=ckeditor_uploader.fields.RichTextUploadingField(
                default="Add description"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="roomtype",
            name="max_capacity",
            field=models.PositiveIntegerField(default=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="roomtype",
            name="room_type",
            field=models.CharField(max_length=100),
        ),
    ]
