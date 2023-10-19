# 1. ОПИСАНИЕ

# 2. УСТАНОВКА

**В корне создается файл [.env](.env) в котором:**
```shell
GIT_SSH_PRIVATE_KEY=$(cat путь к токену от гита id_ed)
GIT_AUTH_TOKEN= сам гиттокен
TELEGRAM_BOT_TOKEN= токен бота
TOKEN_ADMIN= ID пользователя администратора
```
The .env файл должен быть помещен в корень каталога проекта рядом с вашим [compose.yaml](compose.yml) файл.