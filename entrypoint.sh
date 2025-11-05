#!/bin/bash
# Запускаем миграции
python manage.py migrate --noinput
# Создаем суперпользователя (для первого запуска)
# Если хочешь, можешь создать здесь стартового суперпользователя
# python manage.py createsuperuser --noinput || true

# Собираем статику
python manage.py collectstatic --noinput

# Запускаем Gunicorn
exec gunicorn --bind 0.0.0.0:8000 ig_parser_project.wsgi:application