from typing import Any, Optional

from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers.fields import AbsoluteURLImageField
from api.serializers.recipe_compact import RecipeCompactSerializer
from core.constants import RECIPES_LIMIT_QUERY_PARAM
from users.models import User


class UserSerializer(DjoserUserSerializer):

    is_subscribed = serializers.SerializerMethodField()
    avatar = AbsoluteURLImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + (
            "is_subscribed",
            "avatar",
        )
        read_only_fields = getattr(
            DjoserUserSerializer.Meta,
            "read_only_fields",
            tuple(),
        ) + ("is_subscribed", "avatar")

    def get_is_subscribed(self, obj: User) -> bool:
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.subscribers.filter(user=request.user).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)

    def to_representation(self, instance: User) -> dict[str, Optional[str]]:
        request = self.context.get("request")
        avatar_url: Optional[str] = None
        if instance.avatar:
            avatar_url = instance.avatar.url
            if request is not None:
                avatar_url = request.build_absolute_uri(avatar_url)
        return {"avatar": avatar_url}


class SubscriptionSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
        read_only_fields = UserSerializer.Meta.read_only_fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj: User) -> list[dict[str, Any]]:
        recipes_limit = self._get_recipes_limit()
        recipes_qs = obj.recipes.order_by("-created_at")
        if recipes_limit is not None:
            recipes_qs = recipes_qs[:recipes_limit]
        serializer = RecipeCompactSerializer(
            recipes_qs,
            many=True,
            context=self.context,
        )
        return serializer.data

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()

    def _get_recipes_limit(self) -> Optional[int]:
        value = self.context.get(RECIPES_LIMIT_QUERY_PARAM)
        if value is None:
            return None
        if isinstance(value, int):
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
