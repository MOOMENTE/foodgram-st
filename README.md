# Foodgram Backend

Бэкенд сервиса «Фудграм» — социальной сети для обмена рецептами и ведения списка покупок.
Приложение предоставляет REST API, соответствующий спецификации из `docs/openapi-schema.yml`,
и готово к интеграции с SPA-интерфейсом, поставляемым вместе с проектом.

## Основные возможности

- регистрация и авторизация пользователей по email с токенами DRF;
- управление профилем, включая загрузку и удаление аватара;
- создание, редактирование и удаление рецептов, добавление ингредиентов в нужном количестве;
- подписки на авторов, избранные рецепты и список покупок с выгрузкой в текстовый файл;
- генерация коротких ссылок на рецепты вида `/s/<код>/`.

## Технологии

- Python 3.12, Django 4.2, Django REST framework, Djoser;
- PostgreSQL (по умолчанию) или SQLite для локальной разработки;
- Docker (готовые файлы лежат в папке `infra`), GitHub Actions.

## Подготовка окружения

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

Создайте файл `.env` в каталоге `backend` (или используйте переменные окружения)
со значениями, подходящими для вашего окружения:

```env
DJANGO_SECRET_KEY=смените-на-свой-ключ
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
DJANGO_USE_SQLITE=true
# Параметры PostgreSQL понадобятся на продакшене
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Далее выполните миграции, создайте администратора и загрузите справочник ингредиентов:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py load_ingredients  # читает data/ingredients.csv
python manage.py runserver
```

## Запуск в Docker

В каталоге `infra` подготовлены конфигурации для контейнеров PostgreSQL, backend, nginx
и фронтенд-сборки. Контейнер `frontend` собирает SPA и завершает работу, оставляя
готовые файлы в каталоге `frontend/build`.

```bash
cd infra
docker compose up --build -d
```

Команда соберёт образы, применит миграции, соберёт статику и запустит Gunicorn.
После запуска проект будет доступен по адресу <http://localhost>, админка —
по <http://localhost/admin/>.

Полезные команды:

```bash
# загрузить ингредиенты
docker compose exec backend python manage.py load_ingredients

# создать суперпользователя
docker compose exec backend python manage.py createsuperuser

# посмотреть логи backend-сервиса
docker compose logs -f backend

# остановить и удалить контейнеры и тома
docker compose down -v
```

По умолчанию используются переменные окружения, подходящие для локального запуска.
Их можно переопределить через файл `.env` рядом с `docker-compose.yml` или напрямую
в командной строке.

## Примеры запросов

### Получить токен авторизации

```
POST /api/auth/token/login/
{
  "email": "chef@example.com",
  "password": "supersecret"
}
→ {"auth_token": "5f1d9d94f8f74f6f8b1c"}
```

### Создать рецепт

```
POST /api/recipes/
Headers: Authorization: Token <token>
{
  "name": "Паста с соусом",
  "text": "Смешайте ингредиенты и готовьте 10 минут.",
  "cooking_time": 10,
  "image": "data:image/png;base64,...",
  "ingredients": [
    {"id": 1, "amount": 150},
    {"id": 5, "amount": 10}
  ]
}
→ 201 Created (тело соответствует схеме RecipeList)
```

### Добавить рецепт в избранное

```
POST /api/recipes/42/favorite/
Headers: Authorization: Token <token>
→ 201 Created, тело соответствует укороченному рецепту
```

### Получить подписки с ограничением рецептов автора

```
GET /api/users/subscriptions/?recipes_limit=2
Headers: Authorization: Token <token>
→ пагинированный список авторов с их последними рецептами
```

### Скачать список покупок

```
GET /api/recipes/download_shopping_cart/
Headers: Authorization: Token <token>
→ attachment "shopping-list.txt" с агрегированными ингредиентами
```

Redoc со всей спецификацией доступен в готовом фронтенде по адресу `/api/docs/`
после запуска `docker compose up` из каталога `infra`.


## Автор проекта
Юсупов Аюбджон — <aybjonju@gmail.com>.