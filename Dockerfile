FROM ubuntu:latest
LABEL authors="stars"

ENTRYPOINT ["top", "-b"]

FROM python:3.10

# Установите Git, чтобы скачать репозиторий GitHub
RUN apt-get update && apt-get install -y git

# Установите переменные окружения
ENV BOT_TOKEN=${BOT_TOKEN}
ENV GIT_AUTH_TOKEN=${GIT_AUTH_TOKEN}
ENV TOKEN_ADMIN=${TOKEN_ADMIN}

# Создайте рабочий каталог внутри контейнера
WORKDIR /app

# Склонируйте репозиторий GitHub
RUN git clone git@github.com:StarMi0/bot_of_legality.git /app
RUN cd /app/head_bot
# Запуск вашего бота
CMD ["python", "/app/head_bot/main.py"]
