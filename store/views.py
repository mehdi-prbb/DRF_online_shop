from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin,  RetrieveModelMixin

from .serializers import CategorySerializer, MobileSerializer
from .models import Category, Mobile, MobileVariety


class CategoryViewSet(RetrieveModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().filter(is_sub=False)


class MobileCategoryViewSet(RetrieveModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        category_pk = self.kwargs['category_pk']
        return Category.objects.filter(sub_category__slug=category_pk).select_related('sub_category')


class MobileViewSet(RetrieveModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    serializer_class = MobileSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        brand_pk = self.kwargs['brand_pk']
        return Mobile.objects.prefetch_related(
            'discount',
            Prefetch(
                'mobile_vars',
                queryset=MobileVariety.objects.select_related('color')
                )
        ).filter(category__slug=brand_pk)
