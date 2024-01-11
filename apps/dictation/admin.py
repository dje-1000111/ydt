"""Model Admin."""
from django.contrib import admin


from .models import Dictation, Practice


class DictationAdmin(admin.ModelAdmin):
    """Model Admin class."""

    prepopulated_fields = {"slug": ("topic",)}
    list_display = [
        "topic",
        "in_production",
    ]


admin.site.register(Dictation, DictationAdmin)


class PracticeAdmin(admin.ModelAdmin):
    """Model Admin class."""

    list_display = [
        "dictation",
        "user",
        "user_current_line",
        "user_rating",
        "is_done",
        "lines",
    ]

    fieldsets = [
        # Allow to show only those fields in admin to create a new entry.
        # By default, we would see the is_task_done field.
        (
            None,
            {
                "fields": [
                    "dictation",
                    "user",
                    "user_current_line",
                    "user_rating",
                    "is_done",
                    "lines",
                ],
            },
        ),
    ]


admin.site.register(Practice, PracticeAdmin)
