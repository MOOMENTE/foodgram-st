from __future__ import annotations

import io
from typing import Iterable, Optional

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCompactSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    UserSerializer,
)
from core.constants import (
    RECIPES_LIMIT_QUERY_PARAM,
    SHOPPING_LIST_FILENAME,
    SHOPPING_LIST_HEADER,
    SHORT_LINK_URL_NAME,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeShortLink,
    ShoppingCart,
)
from users.models import Subscription, User


class UserViewSet(DjoserUserViewSet):

    queryset = User.objects.all().order_by("email")
    serializer_class = UserSerializer
    pagination_class = FoodgramPagination

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (
                djoser_settings.PERMISSIONS.current_user
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {"subscriptions", "subscribe"}:
            return SubscriptionSerializer
        if self.action == "set_avatar":
            return AvatarSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in {"subscriptions", "subscribe"}:
            limit = self._parse_recipes_limit()
            if limit is not None:
                context[RECIPES_LIMIT_QUERY_PARAM] = limit
        return context

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
        url_path="subscriptions",
    )
    def subscriptions(self, request, *args, **kwargs):
        authors = (
            User.objects.filter(subscribers__user=request.user)
            .order_by("email")
        )
        page = self.paginate_queryset(authors)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, *args, **kwargs):
        author = self.get_object()
        if request.method == "POST":
            if author == request.user:
                raise ValidationError("Нельзя подписаться на самого себя.")
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                author=author,
            )
            if not created:
                raise ValidationError("Подписка уже оформлена.")
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).delete()
        if deleted == 0:
            raise ValidationError("Вы не подписаны на этого пользователя.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("put", "delete"),
        permission_classes=(IsAuthenticated,),
        url_path="me/avatar",
    )
    def set_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save(update_fields=("avatar",))
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _parse_recipes_limit(self) -> Optional[int]:
        value = self.request.query_params.get(RECIPES_LIMIT_QUERY_PARAM)
        if value is None:
            return None
        error_message = "Значение должно быть положительным целым числом."
        try:
            limit = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                {RECIPES_LIMIT_QUERY_PARAM: [error_message]}
            ) from exc
        if limit < 1:
            raise ValidationError({RECIPES_LIMIT_QUERY_PARAM: [error_message]})
        return limit


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = (
        Recipe.objects.select_related("author").prefetch_related(
            "recipe_ingredients__ingredient"
        )
    )
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filterset_class = RecipeFilter
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return RecipeReadSerializer
        if self.action in {"create", "update", "partial_update"}:
            return RecipeWriteSerializer
        if self.action in {"favorite", "shopping_cart"}:
            return RecipeCompactSerializer
        return RecipeReadSerializer

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, *args, **kwargs):
        recipe = self.get_object()
        if request.method == "POST":
            return self._handle_post_action(
                Favorite,
                request.user,
                recipe,
                RecipeCompactSerializer,
                self.get_serializer_context(),
            )
        return self._handle_delete_action(Favorite, request.user, recipe)

    @action(
        detail=True,
        methods=("post", "delete"),
        permission_classes=(IsAuthenticated,),
        url_path="shopping_cart",
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = self.get_object()
        if request.method == "POST":
            return self._handle_post_action(
                ShoppingCart,
                request.user,
                recipe,
                RecipeCompactSerializer,
                self.get_serializer_context(),
            )
        return self._handle_delete_action(ShoppingCart, request.user, recipe)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        items = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total=Sum("amount"))
            .order_by("ingredient__name")
        )
        lines = self._build_shopping_list_lines(items)
        content = self._render_shopping_list(lines)
        return self._make_file_response(content)

    @action(
        detail=True,
        methods=("get",),
        permission_classes=(AllowAny,),
        url_path="get-link",
    )
    def get_link(self, request, *args, **kwargs):
        recipe = self.get_object()
        short_link, _ = RecipeShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={"code": RecipeShortLink.generate_unique_code()},
        )
        short_url = request.build_absolute_uri(
            reverse(SHORT_LINK_URL_NAME, args=(short_link.code,))
        )
        return Response({"short-link": short_url})

    @staticmethod
    def _handle_post_action(model, user, recipe, serializer_class, context):
        _, created = model.objects.get_or_create(
            user=user,
            recipe=recipe,
        )
        if not created:
            raise ValidationError("Рецепт уже добавлен.")
        serializer = serializer_class(recipe, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _handle_delete_action(model, user, recipe):
        deleted, _ = model.objects.filter(
            user=user,
            recipe=recipe,
        ).delete()
        if deleted == 0:
            raise ValidationError("Рецепт не найден в списке.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _build_shopping_list_lines(items: Iterable[dict]) -> list[str]:
        return [
            "{name} — {total} {unit}".format(
                name=item["ingredient__name"],
                total=item["total"],
                unit=item["ingredient__measurement_unit"],
            )
            for item in items
        ]

    @staticmethod
    def _render_shopping_list(lines: Iterable[str]) -> str:
        lines = list(lines)
        body = [SHOPPING_LIST_HEADER, ""]
        body.extend(lines)
        if lines:
            body.append("")
        return "\n".join(body)

    @staticmethod
    def _make_file_response(content: str) -> FileResponse:
        buffer = io.BytesIO()
        buffer.write(content.encode("utf-8"))
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=SHOPPING_LIST_FILENAME,
            content_type="text/plain; charset=utf-8",
        )


class RecipeShortLinkRedirectView(View):

    def get(self, request, code: str, *args, **kwargs):
        short_link = get_object_or_404(RecipeShortLink, code=code)
        return redirect(f"/recipes/{short_link.recipe.id}/")
