from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.utils.translation import gettext_lazy as _

from core.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)


class User(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="Никнейм",
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        help_text=_(
            "Не более %(max_length)s символов. Только буквы, цифры и @/./+/-/_"
        ),
        validators=(username_validator,),
        error_messages={
            "unique": _((
                "Пользователь с таким никнеймом уже "
                "зарегистрирован."
            )),
        },
    )
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        error_messages={
            "unique": _((
                "Пользователь с таким адресом электронной почты уже "
                "зарегистрирован."
            )),
        },
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_FIRST_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LAST_NAME_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("email",)

    def __str__(self) -> str:
        return self.email


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="subscriptions",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="subscribers",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата подписки",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("-created_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"),
                name="unique_user_subscription",
            ),
            CheckConstraint(
                check=~Q(user=F("author")),
                name="prevent_self_subscription",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
