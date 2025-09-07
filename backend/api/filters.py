from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.CharFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.CharFilter(
        method="filter_is_in_shopping_cart"
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author")


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
