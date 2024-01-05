import os

import mysql.connector
from mysql.connector import Error

my_host = os.getenv('MYSQL_HOST', 'localhost')
my_user = os.getenv('MYSQL_USER', 'admin')
my_password = os.getenv('DB_ROOT_PASSWORD', 'Qwerty123456')
my_database = "legality"


# Функция для проверки подключения к базе данных
def check_db_connection():
    try:
        connection = mysql.connector.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            database=my_database
        )
        if connection.is_connected():
            print("Успешное подключение к базе данных")
            return True
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return False


# Функция для проверки таблицы и ее создания при отсутствии
def create_table_if_not_exists():
    try:
        connection = mysql.connector.connect(
            host=my_host,
            user=my_user,
            password=my_password,
            database=my_database
        )
        cursor = connection.cursor()

        # SQL-запрос для создания таблицы
        # create_table_query = """
        # CREATE TABLE IF NOT EXISTS user_data (
        #     tg_id INT PRIMARY KEY,
        #     date DATE,
        #     name VARCHAR(255)
        # );
        # """
        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана или уже существует")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


