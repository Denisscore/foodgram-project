[![foodgram-project](https://github.com/Denisscore/foodgram-project/workflows/foodgram/badge.svg)](https://github.com/Denisscore/foodgram-project/actions)

# **Foodgram-project**

http://130.193.35.203/

Дипломный проект программы Яндекс.Практикум **[Python-разработчик](https://praktikum.yandex.ru/backend-developer/)**

Foodgram - онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

При работе над проектом использован стек технологий: **[Django](https://www.djangoproject.com/)**, **[Python](https://www.python.org/)**, **[PostgreSQL](https://www.postgresql.org/)**, **[NGINX](https://nginx.org/)**, **[Docker](https://www.docker.com/)**, **[Docker-Compose](https://docs.docker.com/compose/)**, **[GitHub](https://github.com)**, TDD, код написан в IDE PyCharm 

## Разворачивание проекта

1.  С клонируйте проект

        git clone https://github.com/Denisscore/foodgram-project
    
    В корневой папке находим файл .env.template. Это шаблон файла переменных окружения. По образу и подобию необходимо создать файл .env и заполнить его своими значениями.


2. Запускаем процесс сборки и запуска контейнеров:

        docker-compose up --build

3. Запускаем терминал внутри контейнера:

        docker-compose exec web bash
   


   или для win систем

        winpty docker-compose exec web bash

4. Накатываем миграции:

        python manage.py migrate

5. Создаем пользователя с правами администратора:

        python manage.py createsuperuser

6. Добавляем в базу ингредиенты и теги:

        python manage.py load_product_data

7. Собираем статику:

        python manage.py collectstatic

