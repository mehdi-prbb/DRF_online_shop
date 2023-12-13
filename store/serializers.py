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
        fields = ['id', 'name', 'slug', 'description', 'discount', 'mobile_vars', 'available']



class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.CharField(max_length=50, source='sub_category')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'parent']
