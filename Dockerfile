# Версия питона для запуска образа
FROM python:3.10.11

# Рабочая папка образа
WORKDIR /app

# Копируем все файлы из локальной папки head_bot в контейнер
COPY ./head_bot /app

# Устанавливаем зависимости из req.txt
RUN pip install --no-cache-dir -r req.txt

# Команды выполняемые при перезагрузке
CMD ["python", "/app/main.py"]