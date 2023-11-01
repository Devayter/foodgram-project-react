from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


ROLES = (
    ('user', 'пользователь'),
    ('admin', 'администратор')
)


class User(AbstractUser):
    '''Модель пользователя'''
    username = models.CharField(
        blank=False,
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message=(
                    'Имя пользователя может содержать только буквы и цифры'
                    ),
                code='invalid_field',
            )
        ],
        verbose_name='Логин'
    )
    name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Фамилия пользователя'
    )
    email = models.EmailField(
        blank=False,
        max_length=300,
        unique=True,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        choices=ROLES,
        blank=False,
        default='user',
        max_length=50,
        verbose_name='Уровень доступа'
    )

    class Meta:
        ordering = ['username', ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
