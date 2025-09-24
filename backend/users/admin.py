from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "recipe_count",
        "subscriber_count",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("username", "first_name", "last_name", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "avatar",
                ),
            },
        ),
    )

    @admin.display(description="Рецептов")
    def recipe_count(self, obj: User) -> int:
        return obj.recipes.count()

    @admin.display(description="Подписчиков")
    def subscriber_count(self, obj: User) -> int:
        return obj.subscribers.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ("user", "author", "created_at")
    search_fields = (
        "user__email",
        "user__username",
        "author__email",
        "author__username",
    )
    list_filter = ("created_at",)
    autocomplete_fields = ("user", "author")
