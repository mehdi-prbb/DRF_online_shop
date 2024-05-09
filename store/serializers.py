from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import (Cart, CartItem, Category, CommentLike,
                    Customer, Laptop, Mobile, Comment,
                    Image, Order, OrderItem, Variety
                    )


class VaritySerializer(serializers.ModelSerializer):

    class Meta:
        model = Variety
        fields = ['unit_price', 'inventory', 'color_code', 'color_name']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']


class MobilesListSerializer(serializers.HyperlinkedModelSerializer):
    varieties = VaritySerializer(many=True)
    images = ImageSerializer(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='mobile-detail', lookup_field='slug')

    class Meta:
        model = Mobile
        fields = ['url', 'name', 'description',
                  'sim_card_number', 'internal_memory',
                  'ram','images','varieties',
                  'discount', 'available']
    

class MobileDetailSerializer(serializers.ModelSerializer):
    varieties = VaritySerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = Mobile
        fields = ['id', 'name', 'description',
                  'networks', 'memory_card_support',
                  'sim_card_number', 'sim_description',
                  'backs_camera', 'internal_memory',
                  'ram', 'video_format_support',
                  'size', 'screen_size', 'screen_size',
                  'picture_resolution','screen_technology',
                  'accessories', 'images','varieties',
                  'discount', 'available']
        

class laptopListSerializer(serializers.HyperlinkedModelSerializer):
    varieties = VaritySerializer(many=True)
    images = ImageSerializer(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='laptop-detail', lookup_field='slug')

    class Meta:
        model = Laptop
        fields = ['url', 'name', 'description',
                  'cpu', 'internal_memory',
                  'ram','images','varieties',
                  'discount', 'available']
    

class LaptopDetailSerializer(serializers.ModelSerializer):
    varieties = VaritySerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = Laptop
        fields = ['id', 'name', 'description',
                  'cpu', 'internal_memory','ram', 
                  'gpu','battery_type', 'weight', 'screen_size',
                  'screen_resolution','dimensions', 'os_type', 'connections',
                  'accessories', 'images','varieties',
                  'discount', 'available']


class CommentsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'title', 'body', 'owner',
                  'datetime_created', 'likes_count',
                  'dislikes_count']

    def get_owner(self, obj):
        if obj.owner.first_name and obj.owner.last_name:
            return f'{obj.owner.first_name} {obj.owner.last_name}'
        if obj.owner.first_name:
            return f'{obj.owner.first_name}'
        if obj.owner.last_name:
            return f'{obj.owner.last_name}'
        if obj.owner.username:
            return f'{obj.owner.username}'
        return 'Anonymous user'
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.count()
    

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['user', 'comment']
        read_only_fields = ['user', 'comment']


class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['user', 'comment']
        read_only_fields = ['user', 'comment']


class SecondLevelSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class FirstLevelSubCategorySerializer(serializers.ModelSerializer):
    subsets = SecondLevelSubCategorySerializer(many=True, source='sub_cat')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'subsets']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.sub_cat.exists():
            data.pop('subsets')
        return data


class CategoriesSerializer(serializers.ModelSerializer):
    subsets = FirstLevelSubCategorySerializer(many=True, source='sub_cat')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'subsets']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.sub_cat.exists():
            data.pop('subsets')
        return data


class UpdateCartItemserializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate(self, data):
        cart_id = self.context['cart_pk']
        object_id = self.instance.object_id  # Fetch the existing object_id
        content_type = self.instance.content_type

        # Your existing code for quantity validation

        # Ensure that the existing quantity is considered when validating
        inventory_data = content_type.get_object_for_this_type(id=object_id).varieties.values('inventory').first()
        inventory = inventory_data['inventory']

        
        if data['quantity'] > inventory:
            raise serializers.ValidationError('Quantity exceeds available inventory.')

        return data


class CartItemVaritySerializer(serializers.ModelSerializer):

    class Meta:
        model = Variety
        fields = ['unit_price', 'color_name', 'color_code']


class AddCartItemSerialize(serializers.ModelSerializer):
    variety_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'content_type', 'object_id', 'quantity', 'variety_id']

    ALLOWED_MODELS = ['mobile', 'laptop']
        

    def validate(self, data):
        cart_id = self.context['cart_pk']
        object_id = data.get('object_id')
        content_type = data.get('content_type')
        variety_id = data.get('variety_id')

        model_name = content_type.model
        if model_name not in self.ALLOWED_MODELS:
            raise serializers.ValidationError('Invalid content type.')

        try:
            product_instance = content_type.get_object_for_this_type(id=object_id)
            valid_varieties = product_instance.varieties.values_list('id', flat=True)
            if variety_id not in valid_varieties:
                raise serializers.ValidationError('Invalid variety for the product.')
            
            variety_instance = Variety.objects.get(id=variety_id)

            variety_inventory = variety_instance.inventory

            existing_quantity_variety = CartItem.objects.filter(
                object_id = object_id,
                cart_id=cart_id,
                variety_id=variety_id
            ).values_list('quantity', flat=True).first()
            
            if existing_quantity_variety is not None:
                if existing_quantity_variety + data['quantity'] > variety_inventory:
                    raise serializers.ValidationError('Quantity exceeds available inventory,')
            elif data['quantity'] > variety_inventory:
                raise serializers.ValidationError('Quantity exceeds available inventory,')
            
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Product not found.')
        
        return data

    def create(self, validated_data):
        cart_id = self.context['cart_pk']

        object_id = validated_data.get('object_id')
        content_type = validated_data.get('content_type')
        quantity = validated_data.get('quantity')
        variety_id = validated_data.get('variety_id')

        try:
            cart_item = CartItem.objects.get(
                                    cart_id=cart_id, object_id=object_id,
                                    content_type=content_type, variety_id=variety_id
                                )
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

        self.instance = cart_item
        return cart_item




class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='content_object.name')
    variety = CartItemVaritySerializer()
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'quantity', 'name', 'variety', 'item_total_price']
    
    def get_item_total_price(self, item):
        return item.quantity * item.variety.unit_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'cart_total_price']
        read_only_fields = ['id']
    
    def get_cart_total_price(self, cart):
        return sum([item.quantity * item.variety.unit_price for item in cart.items.all()])
    

class OrderItemVaritySerializer(serializers.ModelSerializer):

    class Meta:
        model = Variety
        fields = ['unit_price', 'color_name', 'color_code']


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='content_object.name')
    variety = OrderItemVaritySerializer()
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'variety', 'item_total_price']

    def get_item_total_price(self, item):
        return item.quantity * item.variety.unit_price


class OrderCustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, source='user.username')
    phone_number = serializers.CharField(max_length=11, source='user.phone_number')

    class Meta:
        model = Customer
        fields = ['username','phone_number']

 
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = OrderCustomerSerializer(read_only=True)
    order_total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_code', 'customer', 'status', 'datetime_created', 'items', 'order_total_price']

    def get_order_total_price(self, order):
        return sum([item.quantity * item.variety.unit_price for item in order.items.all()])


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField(write_only=True)

        
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('Ther is no cart with this cat id.')

        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is empty.')
        
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.select_related('user').get(user_id=user_id)

            order = Order()
            order.customer = customer
            order.save()

            cart_items = CartItem.objects.select_related('content_type', 'variety').filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    content_type=cart_item.content_type,
                    object_id=cart_item.object_id,
                    quantity=cart_item.quantity,
                    variety=cart_item.variety
                ) for cart_item in cart_items
            ]


            OrderItem.objects.bulk_create(order_items)

            order = Order.objects.prefetch_related(
                'items__content_object',
                'items__variety'
                ).select_related('customer__user').get(pk=order.pk)

            Cart.objects.get(id=cart_id).delete()

            return order