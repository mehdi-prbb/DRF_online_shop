from django.db.models import Prefetch

from .models import Mobile, MobileVariety


def get_mobile_queryset():
    # This function manages mobile queryset for its views.
    return Mobile.objects.prefetch_related(
        'discount',
        'mobile_images',
        Prefetch(
            'mobile_vars',
            queryset=MobileVariety.objects.select_related('color')
            )
    )