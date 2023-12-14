import os

import mysql.connector

db_config = {
    'host': os.environ["BOT_TOKEN"],
    'user': os.environ["BOT_TOKEN"],
    'password': os.environ["BOT_TOKEN"],
    'database': os.environ["BOT_TOKEN"],
}


def user_exists(user_id):
    global connection
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        return result is not None
    except Exception as e:
        print(f"Error checking if user exists: {e}")
        return False
    finally:
        if connection:
            connection.close()


def add_user(user_id, role, registration_data):
    global connection
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "INSERT INTO users (user_id, role, registration_data) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, role, registration_data))

        connection.commit()
    except Exception as e:
        print(f"Error adding user: {e}")
    finally:
        if connection:
            connection.close()


# Создаем таблицу 'users' в базе данных, если она еще не существует
def create_db():
    global connection
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "CREATE TABLE IF NOT EXISTS users (user_id INT PRIMARY KEY, role VARCHAR(255), registration_data TEXT)"
        cursor.execute(query)

        connection.commit()
    except Exception as e:
        print(f"Error creating database table: {e}")
    finally:
        if connection:
            connection.close()


# Вызываем функцию create_db() один раз, чтобы создать таблицу при первом запуске
create_db()