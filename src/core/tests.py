from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Role, Permission, Resource, Action

class AuthTests(APITestCase):
    """
    Тесты для аутентификации, регистрации, профиля и выхода из системы.
    """

    def setUp(self):
        # URLs
        self.register_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('auth_profile')
        self.logout_url = reverse('auth_logout')
        self.secret_url = reverse('secret_document')

        # Данные пользователя
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        # Суперпользователь
        self.superuser_data = {
            'email': 'super@example.com',
            'password': 'superpassword123'
        }
        self.superuser = CustomUser.objects.create_superuser(**self.superuser_data)

    def test_user_registration(self):
        """
        Проверка успешной регистрации пользователя.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2) # 1 superuser, 1 new user
        self.assertTrue(CustomUser.objects.filter(email=self.user_data['email']).exists())

    def test_user_login(self):
        """
        Проверка успешного входа пользователя и получения токенов.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_inactive(self):
        """
        Проверка, что неактивный пользователь не может войти.
        """
        user = CustomUser.objects.create_user(email='inactive@test.com', password='password')
        user.is_active = False
        user.save()
        login_data = {'email': 'inactive@test.com', 'password': 'password'}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_profile_view_and_update(self):
        """
        Проверка просмотра и обновления профиля.
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], self.user_data['email'])

        # Обновление
        update_data = {'first_name': 'Updated', 'last_name': 'Name'}
        update_response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['first_name'], 'Updated')

    def test_soft_delete(self):
        """
        Проверка "мягкого" удаления пользователя (деактивации).
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        delete_response = self.client.delete(self.profile_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        user = CustomUser.objects.get(email=self.user_data['email'])
        self.assertFalse(user.is_active)

        # Проверка, что пользователь больше не может залогиниться
        login_response_after_delete = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response_after_delete.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_logout(self):
        """
        Проверка выхода из системы (добавление refresh токена в черный список).
        """
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {'email': self.user_data['email'], 'password': self.user_data['password']}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(self.logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        # Попытка обновить токен с помощью заблокированного refresh токена
        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionsTests(APITestCase):
    """
    Тесты для кастомной системы прав доступа.
    """

    def setUp(self):
        # URLs
        self.secret_url = reverse('secret_document')
        self.login_url = reverse('token_obtain_pair')

        # Объекты для прав доступа
        self.resource = Resource.objects.create(name='SecretDocument')
        self.action = Action.objects.create(name='read')
        self.permission = Permission.objects.create(resource=self.resource, action=self.action)
        
        # Роли
        self.user_role = Role.objects.create(name='RegularUser')
        self.viewer_role = Role.objects.create(name='DocumentViewer')
        self.viewer_role.permissions.add(self.permission)

        # Пользователи
        self.regular_user = CustomUser.objects.create_user(email='user@example.com', password='password')
        self.regular_user.roles.add(self.user_role)

        self.viewer_user = CustomUser.objects.create_user(email='viewer@example.com', password='password')
        self.viewer_user.roles.add(self.viewer_role)

        self.superuser = CustomUser.objects.create_superuser(email='super@example.com', password='password')

    def test_unauthenticated_access(self):
        """
        Неаутентифицированный пользователь должен получать 401.
        """
        response = self.client.get(self.secret_url)
        # DRF по умолчанию возвращает 401 для IsAuthenticated, и наш HasPermission тоже
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_denied_for_user_without_permission(self):
        """
        Пользователь без нужных прав должен получать 403.
        """
        login_data = {'email': self.regular_user.email, 'password': 'password'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(self.secret_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_granted_for_user_with_permission(self):
        """
        Пользователь с нужными правами должен получать 200.
        """
        login_data = {'email': self.viewer_user.email, 'password': 'password'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(self.secret_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('secret', response.data)

    def test_superuser_access_granted(self):
        """
        Суперпользователь должен иметь доступ всегда.
        """
        login_data = {'email': self.superuser.email, 'password': 'password'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(self.secret_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminAPITests(APITestCase):
    """
    Тесты для API администрирования ролей.
    """
    def setUp(self):
        self.roles_url = reverse('role-list')
        self.login_url = reverse('token_obtain_pair')

        self.regular_user = CustomUser.objects.create_user(email='user@example.com', password='password')
        self.superuser = CustomUser.objects.create_superuser(email='super@example.com', password='password')

    def test_non_superuser_cannot_access_admin_api(self):
        """
        Обычный пользователь не должен иметь доступ к API ролей.
        """
        login_data = {'email': self.regular_user.email, 'password': 'password'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(self.roles_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_superuser_can_create_role(self):
        """
        Суперпользователь может создавать новую роль.
        """
        login_data = {'email': self.superuser.email, 'password': 'password'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        role_data = {'name': 'New Role'}
        response = self.client.post(self.roles_url, role_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name='New Role').exists())