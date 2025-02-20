import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# bot tokens and id's
BOT_TOKEN = os.getenv('BOT_TOKEN')
group_ID = os.getenv('CONSULT_GROUP_ID')

# sql data
my_host = os.getenv('MYSQL_HOST')
my_user = os.getenv('MYSQL_USER')
my_password = os.getenv('DB_ROOT_PASSWORD')
my_database = os.getenv('MYSQL_DATABASE')

# Redis
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = 6379

# URL's
DATABASE_URL = f"mysql+aiomysql://{my_user}:{my_password}@{my_host}/{my_database}"
DATABASE_URL_CREATE = f"mysql+aiomysql://{my_user}:{my_password}@{my_host}/{my_database}"

