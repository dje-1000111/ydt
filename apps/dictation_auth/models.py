"""Auth Models."""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user."""

    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)
    db_table = "auth_user"
