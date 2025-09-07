import json
import os

from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импорт данных об ингредиентах из JSON-файла"

    def handle(self, *args, **kwargs):
        json_file_path = os.path.join("data", "ingredients.json")

        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                ingredients_data = json.load(json_file)

            Ingredient.objects.all().delete()
            total_items = len(ingredients_data)

            progress_bar = tqdm(
                ingredients_data,
                total=total_items,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} "
                "[{elapsed}<{remaining}]",
                desc="Загрузка ингредиентов",
            )

            created_count = 0
            for ingredient_item in progress_bar:
                ingredient_name = ingredient_item.get("name")
                unit = ingredient_item.get("measurement_unit")

                if ingredient_name and unit:
                    _, created = Ingredient.objects.get_or_create(
                        name=ingredient_name, measurement_unit=unit
                    )
                    if created:
                        created_count += 1

                progress = 100 * (progress_bar.n / total_items)
                progress_bar.set_postfix({"Прогресс": f"{progress:.1f}%"})

            self.stdout.write(
                self.style.SUCCESS(
                    f"Завершено! Успешно загружено {created_count} "
                    f"ингредиентов из {total_items} записей."
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Ошибка при загрузке данных: {str(e)}")
            )
