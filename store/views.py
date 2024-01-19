from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .permissions import IsOwnerOrReadonly
from .utils import get_mobile_queryset
from .filters import MobileFilter
from .serializers import CategoriesSerializer, CommentsSerializer, MobileSerializer, SubCategorySerializer
from .models import Category, Comment, Mobile


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = MobileFilter
    queryset = get_mobile_queryset()
    lookup_field = 'slug'


class MobilesByBrand(ListAPIView):
    """
    Returns the list of mobiles by brands.
    """
    serializer_class = MobileSerializer

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return get_mobile_queryset().filter(category__slug=category_slug)
        

class CommentsViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  ListModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """
    A class to leave, list, retrieve and delete comments.
    """
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    ordering = ['-datetime_created']

    def get_queryset(self):
        mobile_slug = self.kwargs['mobile_slug']
        mobile = get_object_or_404(Mobile, slug=mobile_slug)
        return Comment.objects.filter(content_type__model='mobile', object_id=mobile.id, status='a').\
            order_by('-datetime_created').select_related('owner')

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsOwnerOrReadonly()]
        return super().get_permissions()

    def get_serializer_context(self):
        return {
            'mobile_slug': self.kwargs['mobile_slug'],
            'user': self.request.user
            }
    