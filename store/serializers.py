from rest_framework import serializers

from .models import Category, Color, Mobile, Comment, Image, Variety


class MobileColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'code']


class VaritySerializer(serializers.ModelSerializer):
    color = MobileColorSerializer()

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


