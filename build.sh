#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Устанавливаем все зависимости
pip install -r requirements.txt

# 2. Собираем статику (CSS/JS админки)
python manage.py collectstatic --noinput

# 3. Применяем миграции (обновляем БД)
python manage.py migrate