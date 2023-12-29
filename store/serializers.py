from rest_framework import serializers

from .models import Category, Color, Mobile, MobileVariety


class MobileColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'code']


class MobileVaritySerializer(serializers.ModelSerializer):
    color = MobileColorSerializer()

    class Meta:
        model = MobileVariety
        fields = ['unit_price', 'inventory', 'color']


class MobileSerializer(serializers.ModelSerializer):
    mobile_vars = MobileVaritySerializer(many=True)

    class Meta:
        model = Mobile
        fields = ['id', 'name', 'slug',
                  'description', 'picture_resolution',
                  'os_version', 'screen_technology', 'accessories',
                  'discount', 'mobile_vars', 'available']


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


