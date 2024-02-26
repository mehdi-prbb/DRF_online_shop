from django.db.models import Prefetch
from django.contrib.contenttypes.prefetch import GenericPrefetch
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from .permissions import IsOwnerOrReadonly
from .filters import MobileFilter
from .serializers import AddCartItemSerialize, CartItemSerializer, CartSerializer, CategoriesSerializer, CommentsSerializer, MobileSerializer, SubCategorySerializer, UpdateCartItemserializer
from .models import Cart, CartItem, Category, Color, Comment, Mobile, Variety


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
    lookup_field = 'slug'

    def get_queryset(self):
        return Mobile.objects.prefetch_related('discount', 'images',
            Prefetch(
                'varieties',
                queryset=Variety.objects.select_related('color')
                )
            )


class MobilesByBrand(ListAPIView):
    """
    Returns the list of mobiles by brands.
    """
    serializer_class = MobileSerializer

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        return Mobile.objects.prefetch_related('discount', 'images',
            Prefetch(
                'varieties',
                queryset=Variety.objects.select_related('color')
                )
            ).filter(category__slug=category_slug)
        

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
        return mobile.comments.filter(status='a').\
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
    

class CartItemViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_pk).\
            prefetch_related('content_object',
                            Prefetch(
                                'variety',
                                queryset=Variety.objects.select_related('color')
                            )
                            )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerialize
        elif self.request.method == 'PATCH':
            return UpdateCartItemserializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}
    


class CartViewSet(CreateModelMixin,
                RetrieveModelMixin,
                DestroyModelMixin,
                GenericViewSet
                ):
    serializer_class = CartSerializer
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'

    def get_queryset(self):
        return Cart.objects.prefetch_related(
            'items__variety__color',
            'items__content_object'
            )