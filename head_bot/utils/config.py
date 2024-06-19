import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv('BOT_TOKEN')
my_host = os.getenv('MYSQL_HOST', '77.232.134.200')
my_user = os.getenv('MYSQL_USER', 'root')
my_password = os.getenv('DB_ROOT_PASSWORD', 'MYSQL_ROOT_PASSWORD')
my_database = os.getenv('MYSQL_DATABASE', 'MYSQL_DATABASE')
bot_db = os.getenv('BOT_DB', 'BOT_DB')


group_ID = {
    "consult_group_id": os.environ["CONSULT_GROUP_ID"],
    "auto_consult_id": os.environ["AUTO_GROUP_ID"],
    "audit_id": os.environ["AUDIT_GROUP_ID"],
    "all_consult_id": os.environ["ALL_CONSULT_ID"]
}

redis_host = 'redis://localhost'
redis_port = 6379

DATABASE_URL = f"postgresql+asyncpg://{my_user}:{my_password}@{my_host}/{bot_db}"


ADMIN_CHAT_ID = -4258643755