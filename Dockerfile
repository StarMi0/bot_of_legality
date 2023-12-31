FROM python:3.10
LABEL authors="Ramzan"
LABEL maintainer="Legality_bot"

# Установите Git, чтобы скачать репозиторий GitHub
RUN apt-get update && apt-get install -y git

# Создайте рабочий каталог внутри контейнера
WORKDIR /app

# BOT tokens and data
ENV BOT_TOKEN=${BOT_TOKEN}
ENV GIT_AUTH_TOKEN=${GIT_AUTH_TOKEN}
ENV TOKEN_ADMIN=${TOKEN_ADMIN}
# DB data
ENV MYSQL_NAME=${MYSQL_DATABASE}
ENV MYSQL_HOST=${MYSQL_HOST}
ENV MYSQL_USER=${MYSQL_USER}
ENV DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
ENV BOT_TOKEN=${BOT_TOKEN}
# Group ID's
ENV CONSULT_GROUP_ID=${CONSULT_GROUP_ID}
ENV AUTO_GROUP_ID=${AUTO_GROUP_ID}
ENV AUDIT_GROUP_ID=${AUDIT_GROUP_ID}
ENV ALL_CONSULT_ID=${ALL_CONSULT_ID}

COPY ./head_bot /app

# Устанавливаем зависимости из requirements.txt
RUN cd /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Запуск вашего бота
CMD ["python", "/app/main.py"]
