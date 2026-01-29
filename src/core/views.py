from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import CustomUser, Role, Permission, Resource, Action
from .serializers import (
    RegisterSerializer, UserSerializer, RoleSerializer,
    PermissionSerializer, ResourceSerializer, ActionSerializer
)
from .permissions import IsSuperUser, HasPermission


class RegisterView(generics.CreateAPIView):
    """
    Представление для регистрации нового пользователя.
    Доступно для всех.
    """
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LogoutView(generics.GenericAPIView):
    """
    Представление для выхода пользователя из системы (logout).
    Добавляет refresh токен в черный список.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для просмотра и обновления профиля пользователя.
    Доступно только для аутентифицированных пользователей.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        """
        При "удалении" пользователя, он деактивируется (soft delete)
        и все его активные токены добавляются в черный список.
        """
        instance.is_active = False
        instance.save()

        # Добавляем все активные токены пользователя в черный список
        tokens = OutstandingToken.objects.filter(user=instance)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)


class SecretDocumentView(generics.GenericAPIView):
    """
    Тестовое представление для демонстрации работы кастомных прав доступа.
    """
    permission_classes = (HasPermission,)
    required_permission = 'read SecretDocument'

    def get(self, request, *args, **kwargs):
        return Response({"secret": "This is a secret document!"})


# Admin Views
class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления ролями.
    Доступно только для суперпользователей.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsSuperUser,)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра разрешений.
    Доступно только для суперпользователей.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = (IsSuperUser,)


class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления ресурсами.
    Доступно только для суперпользователей.
    """
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsSuperUser,)


class ActionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления действиями.
    Доступно только для суперпользователей.
    """
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = (IsSuperUser,)
