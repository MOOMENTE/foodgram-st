from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeShortLink,
    ShoppingCart,
)


class RecipeIngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = ("name", "author", "cooking_time", "favorites_count")
    search_fields = ("name", "author__email", "author__username")
    list_filter = ("author",)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ("favorites_count",)
    autocomplete_fields = ("author",)

    @admin.display(description="В избранном (шт.)")
    def favorites_count(self, obj: Recipe) -> int:
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = ("user", "recipe", "added_at")
    search_fields = ("user__email", "recipe__name")
    list_filter = ("added_at",)
    autocomplete_fields = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ("user", "recipe", "added_at")
    search_fields = ("user__email", "recipe__name")
    list_filter = ("added_at",)
    autocomplete_fields = ("user", "recipe")


@admin.register(RecipeShortLink)
class RecipeShortLinkAdmin(admin.ModelAdmin):

    list_display = ("code", "recipe", "created_at")
    search_fields = ("code", "recipe__name")
    autocomplete_fields = ("recipe",)
