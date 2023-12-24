from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin,  RetrieveModelMixin
from django_filters.rest_framework import DjangoFilterBackend


from .filters import MobileFilter
from .serializers import CategorySerializer, MobileSerializer, SubCategorySerializer
from .models import Category, Mobile, MobileVariety


class CategoryViewSet(ListModelMixin,
                    GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_sub=False).prefetch_related('sub_cat')
    lookup_field = 'slug'


class MobileCategoryViewSet(ListModelMixin,
                    GenericViewSet):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_sub=True).prefetch_related('sub_cat')


class MobileViewSet(RetrieveModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    serializer_class = MobileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MobileFilter
    lookup_field = 'slug'

    def get_queryset(self):
        quertset = Mobile.objects.prefetch_related(
            'discount',
            Prefetch(
                'mobile_vars',
                queryset=MobileVariety.objects.select_related('color')
                )
        )

        category_slug_parameter = self.request.query_params.get('search')

        if category_slug_parameter is not None:
            quertset = quertset.filter(category__slug=category_slug_parameter)
        return quertset
