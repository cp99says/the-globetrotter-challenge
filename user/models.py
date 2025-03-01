from django.db import models
from uuid6 import uuid7


class UserType(models.TextChoices):
    GUEST = "guest", "Guest"
    REGISTERED = "registered", "Registered"


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    username = models.CharField(max_length=100, unique=True)
    user_type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.GUEST
    )
