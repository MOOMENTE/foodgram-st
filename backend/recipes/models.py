import secrets
import string

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.constants import (
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH,
    MAX_RECIPE_NAME_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    SHORT_CODE_LENGTH,
)


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_RECIPE_NAME_LENGTH,
    )
    image = models.ImageField(
        verbose_name="Фотография",
        upload_to="recipes/images/",
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="RecipeIngredient",
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (мин)",
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                (
                    "Время приготовления должно быть "
                    f"не меньше {MIN_COOKING_TIME} минуты."
                ),
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                (
                    "Время приготовления не может превышать "
                    f"{MAX_COOKING_TIME} минут."
                ),
            ),
        ),
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at", "name")

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                (
                    "Количество должно быть не меньше "
                    f"{MIN_INGREDIENT_AMOUNT}."
                ),
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                (
                    "Количество должно быть не больше "
                    f"{MAX_INGREDIENT_AMOUNT}."
                ),
            ),
        ),
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"
        default_related_name = "recipe_ingredients"
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            ),
        )

    def __str__(self) -> str:
        return f"{self.ingredient} в {self.recipe}"


class Favorite(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    added_at = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("-added_at",)
        default_related_name = "favorites"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_recipe_favorite",
            ),
        )

    def __str__(self) -> str:
        return f"{self.recipe} в избранном у {self.user}"


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    added_at = models.DateTimeField(
        verbose_name="Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Позиция в списке покупок"
        verbose_name_plural = "Список покупок"
        ordering = ("-added_at",)
        default_related_name = "shopping_carts"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_recipe_in_cart",
            ),
        )

    def __str__(self) -> str:
        return f"{self.recipe} в списке покупок у {self.user}"


class RecipeShortLink(models.Model):

    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="short_link",
    )
    code = models.CharField(
        verbose_name="Код",
        max_length=SHORT_CODE_LENGTH,
        unique=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Короткая ссылка"
        verbose_name_plural = "Короткие ссылки"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.code} → {self.recipe}"

    @classmethod
    def generate_unique_code(cls) -> str:
        alphabet = string.ascii_letters + string.digits
        while True:
            code = "".join(
                secrets.choice(alphabet) for _ in range(SHORT_CODE_LENGTH)
            )
            if not cls.objects.filter(code=code).exists():
                return code
