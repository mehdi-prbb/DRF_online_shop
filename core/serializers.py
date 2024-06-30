from rest_framework import serializers

from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer

from . models import Profile

class UsercreateSerializer(DjoserUserCreateSerializer):
    """
    Serializer for creating a user with Djoser.
    Includes only email and password fields.
    """
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ['email', 'password']


class UserSerializer(DjoserUserSerializer):
    """
    Serializer for the user model with Djoser.
    Includes only the email field.
    """
    class Meta(DjoserUserSerializer.Meta):
        fields = ['email']


class CustomUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser and associated Profile model.
    Combines user and profile fields for a comprehensive user profile.
    """
    image = serializers.ImageField(source='profiles.image', required=False)
    ssn = serializers.CharField(source='profiles.ssn', required=True)
    phone_number = serializers.CharField(source='profiles.phone_number', required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + (
                            'email', 'username',
                            'first_name', 'last_name',
                            'ssn', 'phone_number', 'image'
                            )
        
    def update(self, instance, validated_data):
        """
         Updates the CustomUser and associated Profile instances.
        """
        profile_data = validated_data.pop('profiles', {})
        image = profile_data.get('image')
        ssn = profile_data.get('ssn')
        phone_number = profile_data.get('phone_number')

        # Ensure the user has an associated profile
        if not hasattr(instance, 'profiles'):
            Profile.objects.create(user=instance)
        
        # Update the user instance with remaining validated data
        instance = super().update(instance, validated_data)

        # Update or delete the profile image
        if image is None and instance.profiles.image:
            instance.profiles.image.delete(save=False)
            instance.profiles.image = None
        elif image is not None:
            instance.profiles.image = image

        # Update the profile fields
        instance.profiles.ssn = ssn
        instance.profiles.phone_number = phone_number
        instance.profiles.save(update_fields=['image', 'ssn', 'phone_number'])

        return instance


