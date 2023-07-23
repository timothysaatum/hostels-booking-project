# Generated by Django 4.1.7 on 2023-07-23 02:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RoomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("ghana_card_number", models.CharField(max_length=50)),
                ("telephone", models.CharField(help_text="0597856551", max_length=20)),
                (
                    "gender",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")], max_length=10
                    ),
                ),
                (
                    "your_emmergency_contact",
                    models.CharField(help_text="0597856551", max_length=20),
                ),
                (
                    "name_of_emmergency_contact",
                    models.CharField(max_length=50, verbose_name="His/Her Name"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Complain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(help_text="0597856551", max_length=10)),
                ("address", models.CharField(max_length=300)),
                ("full_name", models.CharField(max_length=300)),
                ("message", models.TextField()),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(help_text="0597856551", max_length=10)),
                ("address", models.CharField(max_length=300)),
                ("full_name", models.CharField(max_length=300)),
                ("message", models.TextField()),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
