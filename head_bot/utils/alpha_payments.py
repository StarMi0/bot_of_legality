import datetime
import json

import requests


def create_payment(data):
    payment_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
    # Преобразуем дату и время в строку с форматом ISO8601
    payment_date_str = payment_date.strftime("%Y-%m-%dT%H:%M:%S%z")
    data['paymentDate'] = payment_date_str
    # URL для API создания платежей
    url = "https://enter.tochka.com/sandbox/v2/payment/v1.0/order"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer working_token'
    }
    # Отправляем запрос на создание платежа с данными из параметра data
    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers=headers)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Если успешно, возвращаем ответ API
        return response.json()
    else:
        # Если произошла ошибка, выводим статус и текст ответа
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


def get_payment_status(request_id):
    url = f"https://enter.tochka.com/sandbox/v2/payment/v1.0/status/{request_id}"
    print(url)
    headers = {
        'Authorization': 'Bearer working_token'
    }
    # Отправляем запрос на создание платежа с данными из параметра data
    json_data = json.dumps({})

    response = requests.get(url, headers=headers, data=json_data)
    # Проверяем успешность запроса
    if response.status_code == 200:
        # Если успешно, возвращаем ответ API
        return response.json()
    else:
        # Если произошла ошибка, выводим статус и текст ответа
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


# Пример данных для создания платежа
data = {
    "Data": {
        "counterpartyBankBic": "044525104",
        "counterpartyAccountNumber": "40702810840020002504",
        "counterpartyINN": "5001038736",
        "counterpartyName": "ООО \"БАЙКАЛ-СЕРВИС ТК\"",
        "paymentAmount": "700.33",
        "paymentDate": "2018-03-29",
        "paymentNumber": "9191",
        "paymentPurpose": "Оплата по счету № 1 от 01.01.2021. Без НДС",
    }
}

# Вызов функции для создания платежа
# result = create_payment(data)
# print(result)
result = get_payment_status('openapi-775761ae-833d-4bd9-ae3f-c4a4e241ce43')
print(result)



def get_access_token(username, password, client_id, client_secret):
    # URL для получения токена доступа
    token_url = "https://enter.tochka.com/connect/token"

    # Параметры запроса для получения токена доступа
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "payments"  # Запрашиваем доступ к разрешению "payments"
    }

    # Отправляем POST-запрос для получения токена доступа
    response = requests.post(token_url, data=payload)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Возвращаем токен доступа из ответа
        return response.json().get("access_token")
    else:
        # Если произошла ошибка, выводим статус и текст ответа
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


# Пример использования функции для получения токена доступа с разрешением "payments"
# username = "ваш_логин"
# password = "ваш_пароль"
# client_id = "ваш_client_id"
# client_secret = "ваш_client_secret"
#
# access_token = get_access_token(username, password, client_id, client_secret)
# print("Токен доступа:", access_token)
