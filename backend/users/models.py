from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

ROLES = (
    ('user', 'пользователь'),
    ('admin', 'администратор')
)


class BlacklistedToken(models.Model):
    """Модель черного списка токенов доступа"""
    token = models.CharField(max_length=500)
    blacklisted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.token


class Subscribe(models.Model):
    '''Модель подписок'''
    user = models.ForeignKey(
        'User',
        blank=False,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь'
    )
    subscriber = models.ForeignKey(
        'User',
        blank=False,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'subscriber'),
                name='unique_user_subscriber'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class User(AbstractUser):
    '''Модель пользователя'''
    username = models.CharField(
        blank=False,
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Неправильный формат поля'
                    'Допустимы только буквы, цифры и символы @ . + -'
                ),
                code='invalid_field',
            ),
        ],
        verbose_name='Логин'
    )
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        blank=False,
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
