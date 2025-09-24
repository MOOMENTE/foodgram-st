import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = (
        "Загружает список ингредиентов в базу данных из CSV файла."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            help=(
                "Путь к файлу с ингредиентами (по умолчанию "
                "data/ingredients.csv)"
            ),
        )

    def handle(self, *args, **options):
        path = options.get("path")
        if path:
            file_path = Path(path)
        else:
            file_path = (
                Path(settings.BASE_DIR).parent / "data" / "ingredients.csv"
            )
        if not file_path.exists():
            raise CommandError(f"Файл {file_path} не найден.")

        created = 0
        skipped = 0
        with file_path.open(encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 2:
                    skipped += 1
                    continue
                name, unit = (item.strip() for item in row[:2])
                if not name or not unit:
                    skipped += 1
                    continue
                _, was_created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit,
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Загрузка завершена. Новых записей: {created}. "
                    "Пропущено: {skipped}."
                ).format(
                    created=created,
                    skipped=skipped,
                )
            )
        )
