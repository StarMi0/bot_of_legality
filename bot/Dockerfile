FROM python:3.10
LABEL authors="Ramzan"
LABEL maintainer="Legality_bot"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы из текущей директории в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r req.txt
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python", "main.py"]

