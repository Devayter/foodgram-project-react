from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import MAX_LENGTH_150, MAX_LENGTH_254


class Subscribe(models.Model):
    """Модель подписок."""
    author = models.ForeignKey(
        'User',
        max_length=MAX_LENGTH_150,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        'User',
        max_length=MAX_LENGTH_150,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='users_subscribe_prevent_self_follow',
                check=~models.Q(author=models.F('subscriber')),
            ),
            models.UniqueConstraint(
                fields=('author', 'subscriber'),
                name='unique_author_subscriber'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.subscriber} подписан на {self.author}'


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=MAX_LENGTH_150,
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
        max_length=MAX_LENGTH_150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_150,
        verbose_name='Фамилия пользователя'
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_254,
        unique=True,
        verbose_name='Электронная почта'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
