from collections.abc import Mapping
from typing import Iterable

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers.fields import AbsoluteURLImageField
from api.serializers.users import UserSerializer
from core.constants import (
    MAX_INGREDIENT_AMOUNT,
    MIN_INGREDIENT_AMOUNT,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = fields


class IngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(
        source="ingredient.id",
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name",
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = fields


class RecipeIngredientInputSerializer(serializers.Serializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT,
    )


class RecipeReadSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source="recipe_ingredients",
        many=True,
        read_only=True,
    )
    image = AbsoluteURLImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def get_is_favorited(self, obj: Recipe) -> bool:
        return self._check_relation(obj, "favorites")

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        return self._check_relation(obj, "shopping_carts")

    def _check_relation(self, obj: Recipe, manager_name: str) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        manager = getattr(obj, manager_name)
        return manager.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):

    ingredients = RecipeIngredientInputSerializer(many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        read_only_fields = ("id",)

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", {})
        if "image" in initial_data:
            image_value = initial_data.get("image")
            if image_value in (None, "") or (
                isinstance(image_value, str) and not image_value.strip()
            ):
                raise serializers.ValidationError(
                    {"image": ["Изображение обязательно для рецепта."]}
                )
        if self.instance is not None:
            has_ingredients = "ingredients" in attrs
            if not has_ingredients and isinstance(initial_data, Mapping):
                has_ingredients = "ingredients" in initial_data
            if not has_ingredients:
                raise serializers.ValidationError(
                    {"ingredients": ["Нужно указать ингредиенты рецепта."]}
                )
        return attrs

    def validate_ingredients(
        self,
        ingredients: Iterable[dict],
    ) -> Iterable[dict]:
        if not ingredients:
            raise serializers.ValidationError(
                "Нужно выбрать хотя бы один ингредиент."
            )
        ingredient_ids = [item["id"].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return ingredients

    def create(self, validated_data: dict) -> Recipe:
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self._set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is None:
            raise serializers.ValidationError(
                {"ingredients": ["Нужно указать ингредиенты рецепта."]}
            )
        instance.recipe_ingredients.all().delete()
        self._set_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def _set_ingredients(
        self,
        recipe: Recipe,
        ingredients: Iterable[dict],
    ) -> None:
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients
        )
