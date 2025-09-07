import json
import os

from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, RecipeIngredient


UserModel = get_user_model()


class Command(BaseCommand):
    help = "Импорт кулинарных рецептов из JSON-файла"

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join("data", "recipes.json")

        with open(json_file_path, "r", encoding="utf-8") as json_data:
            recipes_collection = json.load(json_data)

        Recipe.objects.all().delete()

        for recipe_entry in recipes_collection:
            recipe_author = UserModel.objects.filter(
                username=recipe_entry["author"]
            ).first()

            if not recipe_author:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пользователь {recipe_entry['author']} не найден."
                    )
                )
                continue

            new_recipe_entry = Recipe.objects.create(
                name=recipe_entry["name"],
                text=recipe_entry["text"],
                cooking_time=recipe_entry["cooking_time"],
                author=recipe_author,
            )

            if recipe_entry.get("image"):
                image_full_path = os.path.join("data", recipe_entry["image"])
                with open(image_full_path, "rb") as image_file:
                    new_recipe_entry.image.save(
                        os.path.basename(image_full_path),
                        ImageFile(image_file),
                        save=True,
                    )

            for ingredient_component in recipe_entry["ingredients"]:
                ingredient_item = Ingredient.objects.filter(
                    name=ingredient_component["name"]
                ).first()

                if ingredient_item:
                    RecipeIngredient.objects.create(
                        recipe=new_recipe_entry,
                        ingredient=ingredient_item,
                        amount=ingredient_component["amount"],
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Добавлен рецепт: "{new_recipe_entry.name}"'
                )
            )
