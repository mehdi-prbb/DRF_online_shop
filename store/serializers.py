
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Cart, CartItem, Category, Color, Mobile, Comment, Image, Variety


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'code']


class VaritySerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = Variety
        fields = ['unit_price', 'inventory', 'color']


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']


class MobileSerializer(serializers.ModelSerializer):
    varieties = VaritySerializer(many=True)
    images = Serializer(many=True)

    class Meta:
        model = Mobile
        fields = ['id', 'name', 'description', 'slug',
                  'networks', 'memory_card_support',
                  'sim_card_number', 'sim_description',
                  'backs_camera', 'internal_memory',
                  'ram', 'video_format_support',
                  'size', 'screen_size', 'screen_size',
                  'picture_resolution','screen_technology',
                  'accessories', 'images','varieties',
                  'discount', 'available']


class CommentsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'title', 'body', 'owner', 'datetime_created']

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
    
    def create(self, validated_data):
        mobile_slug = self.context['mobile_slug']

        try:
            validated_data['content_object'] = Mobile.objects.get(slug=mobile_slug)
        except Mobile.DoesNotExist:
            raise serializers.ValidationError(f"Product with slug {mobile_slug} does not exist.")
        
        validated_data['owner'] = self.context['user']
        return Comment.objects.create(**validated_data)


class SecondLevelSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class FirstLevelSubCategorySerializer(serializers.ModelSerializer):
    sub_cat = SecondLevelSubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'sub_cat']


class CategoriesSerializer(serializers.ModelSerializer):
    subsets = FirstLevelSubCategorySerializer(many=True, source='sub_cat')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'subsets']


class SubCategorySerializer(serializers.ModelSerializer):
    categories = SecondLevelSubCategorySerializer(many=True, source='sub_cat')

    class Meta:
        model = Category
        fields = ['categories']


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
    color = ColorSerializer()

    class Meta:
        model = Variety
        fields = ['unit_price', 'color']


class AddCartItemSerialize(serializers.ModelSerializer):
    variety_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'content_type', 'object_id', 'quantity', 'variety_id']

    ALLOWED_MODELS = ['mobile']
        

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
    name = serializers.SerializerMethodField()
    variety = CartItemVaritySerializer()
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'quantity', 'name', 'variety', 'item_total_price']

    def get_name(self, item):
        return item.name(item)
    
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
