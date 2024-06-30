from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def profile_for_newly_created_user(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a customer profile
    for newly created user.
    """
    if created:
        Customer.objects.create(user=instance)