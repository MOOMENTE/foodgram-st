    # ФУДГРАМ


    ## Описание

    «Фудграм» — это социальная сеть для гурманов и домашних поваров. Публикуйте свои рецепты, сохраняйте понравившиеся, следите за любимыми авторами и легко планируйте покупки с помощью встроенного списка.

    Автор: Юсупов Аюбджон


    ## Технологии:

    БД: PostgreSQL
    Python, Django, Django REST Framework, Djoser


    ## Клонирование проекта

    1. Клонируйте репозиторий проекта:
        ```bash
        git clone https://github.com/WizardryTea/foodgram-st.git
        cd foodgram-st
        ```

    2. Перейдите в созданную директорию:
        ```bash
        cd foodgram-st
        ```


    ## Запуск проекта

    После клонирования проекта следует осуществить запуск. Он может быть:
    №1. В тестовом режиме.
    №2. Полный запуск.


    ### Тестовый запуск проекта

    1. Установите и активируйте виртуальное окружение
        ```bash
        python -m venv env
        source ./env/bin/activate - для Linux
        source ./env/Scripts/activate - для Windows
        ```

    2. Установите зависимости
        ```bash
        pip install -r requirements.txt
        ```

    3. Выполните миграции
        ```bash
        # foodgram-st/backend
        python manage.py migrate
        ```

    4. Создайте суперпользователя:
        ```bash
        python manage.py createsuperuser
        ```

    5.  Загрузите статические файлы:
        ```bash
        python manage.py collectstatic
        ```

    6. Запустите сервер командой:
        ```bash
        python manage.py runserver
        ```


    ### Полный запуск проекта

    1. Создайте файл `.env` в корне проекта со следующими данными (где *** - ваши данные):
        ```env
        SECRET_KEY=***
        ENGINE=django.db.backends.postgresql
        POSTGRES_NAME=foodgram
        POSTGRES_USER=foodgram_user
        POSTGRES_PASSWORD=***
        DB_HOST=db
        DB_PORT=5432
        DEBUG = True
        ALLOWED_HOSTS="localhost, 127.0.0.1, 0.0.0.0"
        CSRF_TRUSTED_ORIGINS="http://localhost, http://127.0.0.1, http://0.0.0.0"
        ```

    ## Сборка и запуск контейнеров

    1. Соберите и запустите контейнеры командой, находясь в папке infra:
        ```bash
        docker compose up -d --build
        ```
        
    2. Выполните миграции:
        ```bash
        docker-compose exec backend python manage.py makemigrations
        docker-compose exec backend python manage.py migrate
        ```

    3. Выполните сборку статических файлов:
        ```bash
        docker-compose exec backend python manage.py collectstatic --noinput
        ```
    4. Заполните базу тестовыми данными:

        4.1. Загрузите список ингредиентов:
            ```bash
            docker-compose exec backend python manage.py load_ingredients
            ```
        4.2. Загрузите данные тестовых пользователей:
            ```bash
            docker-compose exec backend python manage.py load_users
            ```
        4.3. Установите аватары тестовых пользователей:
            ```bash
            docker-compose exec backend python manage.py set_default_avatars
            ```
        4.4. Загрузите рецепты тестовых пользователей:
            ```bash
            docker-compose exec backend python manage.py load_recipes
            ```
        
    5. Создайте суперпользователя:
        ```bash
        docker-compose exec backend python manage.py createsuperuser
        ```


    ## Доступные адреса

    - [http://127.0.0.1](http://127.0.0.1) фронтенд веб-приложения;
    - [http://127.0.0.1/api/docs/](http://127.0.0.1) — спецификация API;
    - [http://127.0.0.1:8000/admin/](http://127.0.0.1) - админ-панель Django.


    ## Доступные страницы

    Проект состоит из следующих страниц:
    - главная;
    - страница входа;
    - страница регистрации;
    - страница рецепта;
    - страница пользователя;
    - страница подписок;
    - избранное;
    - список покупок;
    - создание и редактирование рецепта;
    - страница смены пароля;
    - статическая страница «О проекте»;
    - статическая страница «Технологии».
