from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Subscription, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff_display",
        "is_superuser_display",
    )
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser")

    @admin.display(description="Персонал")
    def is_staff_display(self, obj):
        return format_html("✓" if obj.is_staff else "✗")

    @admin.display(description="Администратор")
    def is_superuser_display(self, obj):
        return format_html("✓" if obj.is_superuser else "✗")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("follower", "author")
    search_fields = ("follower__email", "author__email")
