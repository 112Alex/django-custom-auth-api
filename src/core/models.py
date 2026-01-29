from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей, где email является уникальным идентификатором
    для аутентификации вместо username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        if not email:
            raise ValueError('Поле Email должно быть установлено')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя с заданным email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.
    """
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Определяет, может ли пользователь войти в админ-панель.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Определяет, следует ли считать этого пользователя активным.',
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email


class Resource(models.Model):
    """
    Модель, представляющая ресурс, к которому запрашивается доступ.
    Например, "Документы", "Отчеты" и т.д.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название ресурса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"


class Action(models.Model):
    """
    Модель, представляющая действие, которое можно выполнить над ресурсом.
    Например, "читать", "создавать", "редактировать", "удалять".
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название действия")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"


class Permission(models.Model):
    """
    Модель, объединяющая ресурс и действие, формируя конкретное право доступа.
    Например, "читать Документы".
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="Ресурс")
    action = models.ForeignKey(Action, on_delete=models.CASCADE, verbose_name="Действие")

    def __str__(self):
        return f'{self.action.name} {self.resource.name}'

    class Meta:
        unique_together = ('resource', 'action')
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"


class Role(models.Model):
    """
    Модель роли, которая является набором разрешений.
    Роли присваиваются пользователям.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название роли")
    permissions = models.ManyToManyField(Permission, verbose_name="Разрешения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


# Добавляем связь Many-to-Many к кастомной модели пользователя
CustomUser.add_to_class('roles', models.ManyToManyField(Role, verbose_name="Роли", blank=True))