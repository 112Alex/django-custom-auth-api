from rest_framework import serializers
from .models import CustomUser, Role, Permission, Resource, Action


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        try:
            user_role = Role.objects.get(name='User')
            user.roles.add(user_role)
        except Role.DoesNotExist:
            # В идеале, здесь нужно логировать ошибку,
            # так как роль 'User' должна всегда существовать.
            pass
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя.
    """
    roles = serializers.StringRelatedField(many=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'roles')


class RoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели роли.
    """
    class Meta:
        model = Role
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели разрешений.
    """
    resource = serializers.StringRelatedField()
    action = serializers.StringRelatedField()

    class Meta:
        model = Permission
        fields = ('id', 'resource', 'action')


class ResourceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ресурса.
    """
    class Meta:
        model = Resource
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели действия.
    """
    class Meta:
        model = Action
        fields = '__all__'
