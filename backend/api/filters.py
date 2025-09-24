from django_filters import rest_framework as filters
from rest_framework.request import Request

from recipes.models import Ingredient, Recipe
from users.models import User


class IngredientFilter(filters.FilterSet):

    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)


    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        normalized = value.strip()
        if not normalized:
            return queryset

        case_sensitive_queryset = queryset.filter(name__startswith=normalized)
        if case_sensitive_queryset.exists():
            return case_sensitive_queryset.order_by("name")

        return queryset.filter(name__istartswith=normalized).order_by("name")


class RecipeFilter(filters.FilterSet):

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.NumberFilter(
        method="filter_is_in_shopping_cart",
    )

    class Meta:
        model = Recipe
        fields = (
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def filter_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        user = self._get_user()
        if user is None:
            return queryset.none()
        return queryset.filter(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        user = self._get_user()
        if user is None:
            return queryset.none()
        return queryset.filter(shopping_carts__user=user)

    def _get_user(self):
        request: Request = getattr(self, "request", None)
        if request is None or not request.user.is_authenticated:
            return None
        return request.user
