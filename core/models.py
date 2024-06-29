from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from . managers import CustomUserManager



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='profiles')
    image = models.ImageField(upload_to='profile_images/')
    phone_number = models.CharField(max_length=11)
    ssn = models.CharField()

    def __str__(self):
        return f'{self.user.email}'
    