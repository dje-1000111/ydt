# Generated by Django 5.0 on 2023-12-14 21:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dictation", "0003_remove_dictation_is_done_remove_dictation_user_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="practice",
            old_name="dictation",
            new_name="dictation_id",
        ),
    ]
