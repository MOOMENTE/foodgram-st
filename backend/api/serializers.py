from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from constants import RECIPE_INGREDIENT_MIN_AMOUNT, RECIPE_MIN_LIMIT
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
)
from users.models import Subscription


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, user):
        request_user = self.context["request"].user
        return (
            request_user.is_authenticated
            and user.author.filter(follower=request_user).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов в рецепте
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient.id"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")
        min_value = RECIPE_INGREDIENT_MIN_AMOUNT


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления ингредиентов в рецепте
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient"
    )
    amount = serializers.IntegerField(min_value=RECIPE_INGREDIENT_MIN_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов
    """
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "image",
            "cooking_time",
            "ingredients",
        )
        read_only_fields = ("id",)

    def validate(self, data):
        if not data.get("ingredients"):
            raise serializers.ValidationError(
                {"detail": 'Поле "ingredients" не может быть пустым.'}
            )

        ingredients = data["ingredients"]
        if not isinstance(ingredients, list):
            raise serializers.ValidationError(
                {"detail": 'Поле "ingredients" должно быть списком.'}
            )

        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                {"detail": "Ингредиенты не могут повторяться."}
            )

        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                {"detail": 'Поле "image" не может быть пустым.'}
            )
        return image

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        validated_data["author"] = self.context.get("request").user
        recipe = super().create(validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        instance.ingredients.clear()
        self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients_data
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "image",
            "author",
            "cooking_time",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def _check_existence(self, model, recipe):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return model.objects.filter(user=request.user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        return self._check_existence(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_existence(ShoppingCart, recipe)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribedUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source="recipes.count",
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, author):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipes = author.recipes.all()
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise ValidationError(
                    {
                        "detail": (
                            'Параметр "recipes_limit" должен быть '
                            "целым числом."
                        )
                    }
                )

            if recipes_limit < RECIPE_MIN_LIMIT:
                raise ValidationError(
                    {
                        "detail": (
                            f'Параметр "recipes_limit" должен быть '
                            f"не менее {RECIPE_MIN_LIMIT}."
                        )
                    }
                )

            recipes = author.recipes.all()[:recipes_limit]

        return ShortRecipeSerializer(recipes, many=True).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("follower", "author")
        read_only_fields = ("follower",)

    def validate(self, data):
        if not data.get("author"):
            raise serializers.ValidationError(
                {"detail": 'Поле "author" не может быть пустым.'}
            )

        request = self.context.get("request")
        author = data["author"]
        if author == request.user:
            raise serializers.ValidationError(
                {"detail": "Нельзя подписаться на самого себя."}
            )

        if Subscription.objects.filter(
            follower=request.user, author=author
        ).exists():
            raise serializers.ValidationError(
                {"detail": "Подписка уже оформлена."}
            )

        return data

    def to_representation(self, instance):
        data = SubscribedUserSerializer(
            instance.author, context=self.context
        ).data
        data["is_subscribed"] = True
        return data


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    duplicate_error_message = "Элемент уже существует."

    class Meta:
        abstract = True
        fields = ("user", "recipe")
        read_only_fields = ("user",)

    def validate(self, data):
        if not data.get("recipe"):
            raise serializers.ValidationError(
                {"detail": 'Поле "recipe" не может быть пустым.'}
            )

        user = self.context["request"].user
        recipe = data["recipe"]

        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"detail": self.duplicate_error_message}
            )
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(BaseUserRecipeSerializer):
    duplicate_error_message = "Рецепт уже добавлен в избранное."

    class Meta(BaseUserRecipeSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseUserRecipeSerializer):
    duplicate_error_message = "Рецепт уже добавлен в корзину."

    class Meta(BaseUserRecipeSerializer.Meta):
        model = ShoppingCart
