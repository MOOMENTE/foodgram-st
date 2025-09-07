import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


Account = get_user_model()


class Command(BaseCommand):
    help = "Импорт данных пользователей из JSON-файла"

    def handle(self, *args, **kwargs):
        users_data_path = os.path.join("data", "users.json")

        with open(users_data_path, "r", encoding="utf-8") as json_file:
            user_records = json.load(json_file)

        for account_info in user_records:
            if Account.objects.filter(
                username=account_info["username"]
            ).exists():
                self.stdout.write(
                    f'Аккаунт с именем "{account_info["username"]}"'
                    " уже зарегистрирован"
                )
                continue

            new_account = Account.objects.create_user(
                username=account_info["username"],
                email=account_info["email"],
                first_name=account_info["first_name"],
                last_name=account_info["last_name"],
                password=account_info["password"],
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Добавлен пользователь: {new_account.username} "
                    f"({new_account.first_name} {new_account.last_name})"
                )
            )
