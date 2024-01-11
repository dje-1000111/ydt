"""Admin."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model


UserModel = get_user_model()


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin."""
