from rest_framework import serializers

from .models import Category, Color, Mobile, MobileComment, MobileImage, MobileVariety


class MobileColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'code']


class MobileVaritySerializer(serializers.ModelSerializer):
    color = MobileColorSerializer()

    class Meta:
        model = MobileVariety
        fields = ['unit_price', 'inventory', 'color']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileImage
        fields = ['image']


class MobileSerializer(serializers.ModelSerializer):
    mobile_vars = MobileVaritySerializer(many=True)
    images = ImageSerializer(many=True, source='mobile_images')

    class Meta:
        model = Mobile
        fields = ['id', 'name', 'slug',
                  'description', 'images', 'picture_resolution',
                  'screen_technology', 'accessories',
                  'discount', 'mobile_vars', 'available']


class MobileCommentsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = MobileComment
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
            validated_data['mobile'] = Mobile.objects.get(slug=mobile_slug)
        except Mobile.DoesNotExist:
            raise serializers.ValidationError(f"Mobile with slug '{mobile_slug} does not exist.")
        
        validated_data['owner'] = self.context['user']
        return MobileComment.objects.create(**validated_data)
    


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


