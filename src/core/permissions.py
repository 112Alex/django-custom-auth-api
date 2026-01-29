from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class HasPermission(BasePermission):
    """
    Кастомное право доступа для проверки, имеет ли пользователь необходимое разрешение.
    Разрешение определяется в представлении через `required_permission`.
    """
    def has_permission(self, request, view):
        # Получаем необходимое разрешение из атрибутов представления
        required_permission_str = getattr(view, 'required_permission', None)
        if not required_permission_str:
            # Если в представлении не указано required_permission, доступ запрещен
            return False

        try:
            action_name, resource_name = required_permission_str.split(' ', 1)
        except ValueError:
            # Неверный формат required_permission
            return False

        # Проверяем, аутентифицирован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Суперпользователь имеет доступ ко всему
        if request.user.is_superuser:
            return True

        # Проверяем наличие права у пользователя через его роли
        user_roles = request.user.roles.all()
        for role in user_roles:
            if role.permissions.filter(action__name=action_name, resource__name=resource_name).exists():
                return True

        return False
