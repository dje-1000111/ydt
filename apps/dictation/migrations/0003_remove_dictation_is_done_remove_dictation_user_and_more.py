# Generated by Django 5.0 on 2023-12-14 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dictation", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dictation",
            name="is_done",
        ),
        migrations.RemoveField(
            model_name="dictation",
            name="user",
        ),
        migrations.RemoveField(
            model_name="dictation",
            name="user_current_line",
        ),
        migrations.RemoveField(
            model_name="dictation",
            name="user_rating",
        ),
        migrations.CreateModel(
            name="Practice",
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
                ("user_current_line", models.IntegerField(blank=True, null=True)),
                ("user_rating", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "is_done",
                    models.BooleanField(
                        default=False, verbose_name="is_dictation_done"
                    ),
                ),
                (
                    "dictation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dictation.dictation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
