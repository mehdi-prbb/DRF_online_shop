from django.db.models import Value
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ModelViewSet
from rest_framework.mixins import (ListModelMixin,
                                   RetrieveModelMixin,
                                   DestroyModelMixin,
                                   CreateModelMixin
                                    )
from . import serializers
from . paginations import CustomPagination
from .permissions import IsOwnerOrReadonly
from .models import (Cart, CartItem, Category, HeadPhone, Laptop,
                    Mobile, Order, CommentLike,
                    CommentDislike, Comment
                    )


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
    queryset = Mobile.objects.prefetch_related(
        'discount', 'images', 'varieties')
    filter_backends = [DjangoFilterBackend]
    lookup_field = 'slug'

    def get_queryset(self):
        return Mobile.objects.prefetch_related(
            'discount', 'images', 'varieties')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.MobileDetailSerializer
        return serializers.MobileListSerializer


class MobileByBrandViewSet(ListAPIView):
    """
    Returns the list and details of mobiles and filter them by brands.
    """
    serializer_class = serializers.MobileListSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'detail':'Mobile brand not found.'},
                            status=status.HTTP_404_NOT_FOUND) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        category = self.kwargs['slug']
        return Mobile.objects.prefetch_related(
            'discount', 'images', 'varieties') \
                .filter(category__slug=category)
    

class HeadPhoneViewSet(ReadOnlyModelViewSet):
    """
    Returns the list and details of mobiles and filter them by brands.
    """
    queryset = Mobile.objects.prefetch_related(
        'discount', 'images', 'varieties')
    filter_backends = [DjangoFilterBackend]
    lookup_field = 'slug'

    def get_queryset(self):
        return HeadPhone.objects.prefetch_related(
            'discount', 'images', 'varieties')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.HeadPhoneDetailSerializer
        return serializers.HeadPhoneListSerializer


class HeadPhoneByBrandViewSet(ListAPIView):
    """
    Returns the list and details of mobiles and filter them by brands.
    """
    serializer_class = serializers.HeadPhoneListSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'detail':'Mobile brand not found.'},
                            status=status.HTTP_404_NOT_FOUND) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        category = self.kwargs['slug']
        return HeadPhone.objects.prefetch_related(
            'discount', 'images', 'varieties') \
                .filter(category__slug=category)
    

class LaptopViewSet(ReadOnlyModelViewSet):
    """
    Returns the list and details of laptops and filter them by brands.
    """
    queryset = Laptop.objects.prefetch_related('discount', 'images', 'varieties')
    filter_backends = [DjangoFilterBackend]
    lookup_field = 'slug'

    def get_queryset(self):
        return Laptop.objects.prefetch_related('discount', 'images', 'varieties')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.LaptopDetailSerializer
        return serializers.LaptopListSerializer


class LaptopByBrandViewSet(ListAPIView):
    """
    Returns the list and details of laptops and filter them by brands.
    """
    serializer_class = serializers.LaptopListSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'detail':'Laptop brand not found.'},
                            status=status.HTTP_404_NOT_FOUND) 
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        category = self.kwargs['slug']
        return Laptop.objects.prefetch_related('discount', 'images', 'varieties') \
            .filter(category__slug=category)


class CommentsViewSet(
                    CreateModelMixin,
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
        
        model_mapping = {
            'mobile': Mobile,
            'laptop': Laptop,
            'headphone': HeadPhone
        }
        model_name = self.request.resolver_match.url_name.split('-')[0]
        model_class = model_mapping.get(model_name)
        slug_key = self.kwargs.get(f'{model_name}_slug')

        model_instance = get_object_or_404(model_class, slug=slug_key)
        self.product = model_instance
        return model_instance.comments.filter(status='a').order_by(
            '-datetime_created').select_related(
                'owner', 'content_type') \
                    .prefetch_related('likes', 'dislikes')

    def create(self, request, *args, **kwargs):
        if not hasattr(self, 'product'):
            self.get_queryset()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['content_object'] = self.product
        serializer.validated_data['owner'] = self.request.user
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'],
            serializer_class=serializers.LikeSerializer)
    def like(self, request, *args, **kwargs):
        if not hasattr(self, 'product'):
            self.get_queryset()

        product = self.product
        id = kwargs.get('pk')
        user = request.user
        comment = get_object_or_404(Comment, id=id, object_id=product.id, status='a')
        like = CommentLike.objects.filter(comment=comment, user=user)
        dislike = CommentDislike.objects.filter(comment=comment, user=user)

        if like:
            like.delete()
            return Response({'message': 'unliked.'}, status=status.HTTP_200_OK)
        elif dislike:
            dislike.delete()
            CommentLike.objects.create(comment=comment, user=self.request.user)
            return Response({'message': 'dislike erased and liked.'}, status=status.HTTP_200_OK)
        else:
            CommentLike.objects.create(comment=comment, user=self.request.user)
            return Response({'message': 'liked.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            serializer_class=serializers.DislikeSerializer)
    def dislike(self, request, *args, **kwargs):
        if not hasattr(self, 'product'):
            self.get_queryset()
        
        product = self.product
        id = kwargs.get('pk')
        user = request.user
        comment = get_object_or_404(Comment, id=id, object_id=product.id, status='a')
        dislike = CommentDislike.objects.filter(comment=comment, user=user)
        like = CommentLike.objects.filter(comment=comment, user=user)
        

        if dislike:
            dislike.delete()
            return Response({'message': 'undisliked.'}, status=status.HTTP_200_OK)
        elif like:
            like.delete()
            CommentDislike.objects.create(comment=comment, user=self.request.user)
            return Response({'message': 'like erased and disliked.'}, status=status.HTTP_200_OK)
        else:
            CommentDislike.objects.create(comment=comment, user=self.request.user)
            return Response({'message': 'disliked.'}, status=status.HTTP_200_OK)


    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsOwnerOrReadonly()]
        return super().get_permissions()


class CartItemViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_pk).\
            prefetch_related('content_object', 'variety')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
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


class GlobalSearchView(ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.SearchSerializer

    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get('query', '')
        if not query:
            return Response({'detail': 'not found.'})

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.query_params.get('query', '')

        mobile_queryset = Mobile.objects.filter(name__icontains=query) \
            .values('name', 'slug', 'category__sub_category__title') \
                .annotate(model_name=Value('Mobile'))
        laptop_queryset = Laptop.objects.filter(name__icontains=query) \
            .values('name', 'slug', 'category__sub_category__title') \
                .annotate(model_name=Value('Laptop'))
        headphone_queryset = HeadPhone.objects.filter(name__icontains=query) \
            .values('name', 'slug', 'category__sub_category__title') \
                .annotate(model_name=Value('HeadPhone'))

        # Combine the querysets using the union operator
        combined_queryset = mobile_queryset.union(laptop_queryset, headphone_queryset)

        return combined_queryset
