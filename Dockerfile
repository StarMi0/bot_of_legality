FROM python:3.10
LABEL authors="Ramzan"
LABEL maintainer="Legality_bot"

# Используем Python как базовый образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы из текущей директории в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r req.txt

# Указываем PDF-файл как часть приложения
COPY offer_contract.pdf /app/offer_contract.pdf

# Запускаем бота
CMD ["python", "main.py"]

