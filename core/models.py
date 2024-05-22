from django.db import models
from django.contrib.auth.models import AbstractUser

from . managers import CustomUserManager



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
