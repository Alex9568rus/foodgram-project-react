#rom django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()
# class User(AbstractUser):
#     email = models.EmailField(
#         unique=True,
#         max_length=254,
#         verbose_name='Адрес электронной почты'
#     )
#     first_name = models.CharField(
#         max_length=150,
#         verbose_name='Имя'
#     )
#     last_name = models.CharField(
#         max_length=150,
#         verbose_name='Фамилия'
#     )

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

#     class Meta:
#         ordering = ['id']

#     def __str__(self):
#         return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        null=True,
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор, на которого подписываться',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_links'
            ),
        ]
