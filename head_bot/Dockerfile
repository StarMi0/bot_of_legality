FROM ubuntu:latest
LABEL authors="stars"

ENTRYPOINT ["top", "-b"]

# Версия питона для запуска образа
FROM python:3.10.11

# Копирование файлов проекта
COPY . /head_bot

# Рабочая папка образа
WORKDIR /head_bot

# Рабочая папка окружения
ENV VIRTUAL_ENV=/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV BOT_TOKEN=5536556669:AAHnJXF_UJYb_rME2hZ1Quftj3cTw5HAaV8

# Номер порта для Докер-образа
EXPOSE 8082

# Команды выполняемые при первом запуске контейнера
RUN pip install -r req.txt
RUN python main.py

# Команды выполняемые при перезагрузке
CMD ["python", "main.py"]