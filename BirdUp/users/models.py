from django.urls import reverse
from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    about = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе')
    photo = models.ImageField(
        verbose_name='Фото',
        upload_to='users/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def get_absolute_url(self):
        return reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
