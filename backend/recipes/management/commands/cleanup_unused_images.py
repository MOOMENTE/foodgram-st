import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Recipe
from users.models import User


class Command(BaseCommand):
    help = "Удаление неиспользуемых аватаров и изображений рецептов"

    def handle(self, *args, **options):
        recipe_images = set(
            Recipe.objects.exclude(image="").values_list("image", flat=True)
        )
        avatar_images = set(
            User.objects.exclude(avatar="").values_list("avatar", flat=True)
        )

        avatars_dir = os.path.join(
            settings.MEDIA_ROOT, "data", "images", "avatars"
        )
        recipes_dir = os.path.join(
            settings.MEDIA_ROOT, "data", "images", "recipes"
        )

        if os.path.exists(avatars_dir):
            for filename in os.listdir(avatars_dir):
                file_path = os.path.join("data", "images", "avatars", filename)
                if file_path not in avatar_images:
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    try:
                        os.remove(full_path)
                        self.stdout.write(
                            f"Deleted unused avatar: {file_path}"
                        )
                    except OSError as e:
                        self.stdout.write(f"Error deleting {file_path}: {e}")

        if os.path.exists(recipes_dir):
            for filename in os.listdir(recipes_dir):
                file_path = os.path.join("data", "images", "recipes", filename)
                if file_path not in recipe_images:
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    try:
                        os.remove(full_path)
                        self.stdout.write(
                            f"Deleted unused recipe image: {file_path}"
                        )
                    except OSError as e:
                        self.stdout.write(f"Error deleting {file_path}: {e}")

        self.stdout.write(
            self.style.SUCCESS("Successfully cleaned up unused images")
        )
