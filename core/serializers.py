from django.conf import settings

from rest_framework import serializers

from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer

from . models import Profile, CustomUser

class UsercreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ['email', 'password']


class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = ['email']


class CustomUserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='profiles.image', required=False)
    ssn = serializers.CharField(source='profiles.ssn', required=True)
    phone_number = serializers.CharField(source='profiles.phone_number', required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('email', 'username', 'first_name', 'last_name', 'ssn', 'phone_number', 'image',)
        
    def update(self, instance, validated_data):
    #     # Extract profile data
        profile_data = validated_data.pop('profiles', {})
        image = profile_data.get('image')
        ssn = profile_data.get('ssn')
        phone_number = profile_data.get('phone_number')

        print(profile_data)
        print(image)


        # Ensure the profile exists
        if not hasattr(instance, 'profiles'):
            Profile.objects.create(user=instance)
        
        # Call the parent class's update method to handle the rest of the fields
        instance = super().update(instance, validated_data)

        # Update or delete the profile image if provided
        if image is None and instance.profiles.image:
            # Delete the image if image is set to None
            instance.profiles.image.delete(save=False)
            instance.profiles.image = None
        elif image is not None:
            # Update the profile image
            instance.profiles.image = image

        instance.profiles.ssn = ssn
        instance.profiles.phone_number = phone_number
        instance.profiles.save(update_fields=['image', 'ssn', 'phone_number'])

        return instance


