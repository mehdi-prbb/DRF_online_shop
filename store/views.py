from django.db.models import Prefetch

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from store.utils import get_mobile_queryset
from .filters import MobileFilter
from .serializers import CategoriesSerializer, MobileSerializer, SubCategorySerializer
from .models import Category


class CategoryViewSet(ReadOnlyModelViewSet):
    """
    A class to list all categories and retrieve their subcategories.
    """
    queryset = Category.objects.filter(is_sub=False).prefetch_related(
            Prefetch(
                'sub_cat',
                queryset=Category.objects.prefetch_related('sub_cat')
                )
        )
    lookup_field = 'slug'

    # 
    def get_serializer_class(self):
        if 'slug' in self.kwargs:
            return SubCategorySerializer
        else:
            return CategoriesSerializer


class MobileViewSet(ReadOnlyModelViewSet):
    """
    Returns the list of all mobiles.
    """
    serializer_class = MobileSerializer
    queryset = get_mobile_queryset()
    lookup_field = 'slug'


class MobilesByBrand(ListAPIView):
    """
    Returns the list of all mobiles by brands and selected filters.
    """
    serializer_class = MobileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MobileFilter

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return get_mobile_queryset().filter(category__slug=category_slug)
        
    
class MobileDetails(RetrieveAPIView):
    """
    Returns the details of selected mobiles.
    """
    serializer_class = MobileSerializer
    lookup_field = 'slug'
    queryset = get_mobile_queryset()
