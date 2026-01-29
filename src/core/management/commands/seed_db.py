from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Action, Resource, Permission, Role, CustomUser

class Command(BaseCommand):
    help = 'Seeds the database with initial data for roles and permissions.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Создаем действия
        actions_to_create = ['read', 'write', 'delete']
        actions = {}
        for action_name in actions_to_create:
            action, created = Action.objects.get_or_create(name=action_name)
            actions[action_name] = action
            if created:
                self.stdout.write(self.style.SUCCESS(f'Action "{action_name}" created.'))

        # Создаем ресурсы
        resources_to_create = ['SecretDocument', 'UserProfile']
        resources = {}
        for resource_name in resources_to_create:
            resource, created = Resource.objects.get_or_create(name=resource_name)
            resources[resource_name] = resource
            if created:
                self.stdout.write(self.style.SUCCESS(f'Resource "{resource_name}" created.'))

        # Создаем разрешения
        read_secret_perm, _ = Permission.objects.get_or_create(
            resource=resources['SecretDocument'], action=actions['read']
        )
        write_secret_perm, _ = Permission.objects.get_or_create(
            resource=resources['SecretDocument'], action=actions['write']
        )
        read_profile_perm, _ = Permission.objects.get_or_create(
            resource=resources['UserProfile'], action=actions['read']
        )
        write_profile_perm, _ = Permission.objects.get_or_create(
            resource=resources['UserProfile'], action=actions['write']
        )

        # Создаем роли и назначаем разрешения
        # Роль "Администратор" с полными правами
        admin_role, created = Role.objects.get_or_create(name='Admin')
        if created:
            admin_role.permissions.add(read_secret_perm, write_secret_perm, read_profile_perm, write_profile_perm)
            self.stdout.write(self.style.SUCCESS('Role "Admin" created and all permissions assigned.'))

        # Роль "Пользователь" с ограниченными правами
        user_role, created = Role.objects.get_or_create(name='User')
        if created:
            user_role.permissions.add(read_secret_perm, read_profile_perm)
            self.stdout.write(self.style.SUCCESS('Role "User" created and assigned read permissions.'))

        # Создаем пользователей
        if not CustomUser.objects.filter(email='admin@example.com').exists():
            admin_user = CustomUser.objects.create_superuser('admin@example.com', 'adminpassword')
            admin_user.roles.add(admin_role)
            self.stdout.write(self.style.SUCCESS('Superuser "admin@example.com" created.'))

        if not CustomUser.objects.filter(email='user@example.com').exists():
            user = CustomUser.objects.create_user('user@example.com', 'userpassword')
            user.roles.add(user_role)
            self.stdout.write(self.style.SUCCESS('User "user@example.com" created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete.'))

