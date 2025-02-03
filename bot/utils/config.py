import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# bot tokens and id's
BOT_TOKEN = os.getenv('BOT_TOKEN', '6937575207:AAEyjyd2hEuJCrQPWSTDj7RcN_Me2Wy6cKk')
group_ID = os.getenv('CONSULT_GROUP_ID', '-1002050871811')

# sql data
my_host = os.getenv('MYSQL_HOST', 'localhost')
my_user = os.getenv('MYSQL_USER', 'root')
my_password = os.getenv('DB_ROOT_PASSWORD', '2663520Art')
my_database = os.getenv('MYSQL_DATABASE', 'legality')

# Redis
redis_host = 'redis'
redis_port = 6379

# URL's
DATABASE_URL = f"mysql+aiomysql://{my_user}:{my_password}@{my_host}/{my_database}"
DATABASE_URL_CREATE = f"mysql+aiomysql://{my_user}:{my_password}@{my_host}/{my_database}"

