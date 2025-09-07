import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Устанавливает аватары по умолчанию"

    def handle(self, *args, **options):
        avatar_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
        os.makedirs(avatar_dir, exist_ok=True)

        users = User.objects.all()
        total_users = users.count()

        self.stdout.write(
            f"Начинаем установку аватаров для "
            f"{total_users} пользователей..."
        )

        for user in users:
            avatar_number = user.id % 6 + 1

            for ext in [".png", ".jpg"]:
                default_avatar_path = os.path.join(
                    settings.BASE_DIR,
                    "data",
                    "images",
                    "test-images",
                    f"face{avatar_number}{ext}",
                )

                if os.path.exists(default_avatar_path):
                    new_avatar_path = os.path.join(
                        avatar_dir, f"user_{user.id}_avatar{ext}"
                    )
                    shutil.copy2(default_avatar_path, new_avatar_path)

                    user.avatar = f"avatars/user_{user.id}_avatar{ext}"
                    user.save(update_fields=["avatar"])

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Установлен аватар для пользователя "
                            f"{user.username}"
                        )
                    )
                    break
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Не найден файл аватара для пользователя "
                        f"{user.username}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Установка аватаров завершена"))
