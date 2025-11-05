# Используем образ Python на основе Debian Bookworm
FROM python:3.10-slim-bookworm

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

# Устанавливаем системные зависимости
# libnss3 и т.д. для Playwright. libpq-dev для psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libatspi2.0-0 libgbm1 libasound2 \
    libpq-dev build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Устанавливаем браузеры Playwright
RUN python -m playwright install --with-deps chromium

# Копируем entrypoint и делаем его исполняемым
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Копируем весь код проекта
COPY . /app/

# Открываем порт
EXPOSE 8000

# Запускаем entrypoint.sh при старте контейнера
CMD ["/bin/bash", "/app/entrypoint.sh"]