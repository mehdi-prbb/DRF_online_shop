from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer


class UsercreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ['email', 'password']


class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = ['email']