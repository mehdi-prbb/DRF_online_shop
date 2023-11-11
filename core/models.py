from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True)

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number