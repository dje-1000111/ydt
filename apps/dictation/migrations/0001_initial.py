# Generated by Django 5.0 on 2023-12-14 12:33

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Dictation",
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
                ("video_id", models.CharField(blank=True, max_length=50, null=True)),
                ("filename", models.CharField(blank=True, max_length=200, null=True)),
                ("timestamps", models.JSONField()),
                ("topic", models.CharField(max_length=200)),
                ("level", models.IntegerField()),
                ("tip", models.JSONField()),
                ("slug", models.SlugField(default="")),
                ("user_current_line", models.IntegerField(blank=True, null=True)),
                ("user_rating", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "is_done",
                    models.BooleanField(
                        default=False, verbose_name="is_dictation_done"
                    ),
                ),
            ],
        ),
    ]
