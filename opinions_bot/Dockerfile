FROM ubuntu:latest
LABEL authors="stars"

ENTRYPOINT ["top", "-b"]

# Версия питона для запуска образа
FROM python:3.10.11

# Копирование файлов проекта
COPY . /opinions_bot

# Рабочая папка образа
WORKDIR /opinions_bot

# Рабочая папка окружения
ENV VIRTUAL_ENV=/env
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV BOT_TOKEN=YourToken

# Номер порта для Докер-образа
EXPOSE 8001

# Команды выполняемые при первом запуске контейнера
RUN pip install -r req.txt
RUN python main.py

# Команды выполняемые при перезагрузке
CMD ["python", "main.py"]