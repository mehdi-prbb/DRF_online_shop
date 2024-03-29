from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

from store.filters import MobileFilterSet

from .permissions import IsOwnerOrReadonly
from . import serializers
from .models import Cart, CartItem, Category, Comment, Mobile, Order, OrderItem, Variety


class CategoryViewSet(ListModelMixin, GenericViewSet):
    """
    A class to list all categories and retrieve their subcategories.
    """
    serializer_class = serializers.CategoriesSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_sub=False).prefetch_related(
            Prefetch(
                'sub_cat',
                queryset=Category.objects.prefetch_related('sub_cat')
                )
        )


class MobileViewSet(ReadOnlyModelViewSet):
    """
    Returns the list and details of mobiles and filter them by brands.
    """
    queryset = Mobile.objects.prefetch_related('discount', 'images', 'varieties')
    filter_backends = [DjangoFilterBackend]
    filterset_class = MobileFilterSet
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.MobileDetailSerializer
        return serializers.MobilesListSerializer
    

class CommentsViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  ListModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """
    A class to leave, list, retrieve and delete comments.
    """
    serializer_class = serializers.CommentsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    ordering = ['-datetime_created']

    def get_queryset(self):
        mobile_slug = self.kwargs['mobile_slug']
        mobile = get_object_or_404(Mobile, slug=mobile_slug)
        return mobile.comments.filter(status='a').\
            order_by('-datetime_created').select_related('owner', 'content_type')

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
            prefetch_related('content_object', 'variety')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerialize
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemserializer
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}
    


class CartViewSet(CreateModelMixin,
                RetrieveModelMixin,
                DestroyModelMixin,
                GenericViewSet
                ):
    serializer_class = serializers.CartSerializer
    lookup_value_regex = '[0-9a-fA-F]{8}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{4}\-?[0-9a-fA-F]{12}'

    def get_queryset(self):
        return Cart.objects.prefetch_related(
            'items__variety',
            'items__content_object'
            )
    

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'head', 'options']

    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.prefetch_related(
            'items__variety',
            'items__content_object'
        ).select_related('customer__user').all()
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.OrderCreateSerializer
        return serializers.OrderSerializer
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
    
    def create(self, request, *args, **kwargs):
        create_order_serializer = serializers.OrderCreateSerializer(
            data=request.data,
            context={'user_id': self.request.user.id}
            )
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()

        serializer = serializers.OrderSerializer(created_order)
        return Response(serializer.data)