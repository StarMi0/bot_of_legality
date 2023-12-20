import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

db_config = {
    'host': os.environ["BOT_TOKEN"],
    'user': os.environ["BOT_TOKEN"],
    'password': os.environ["BOT_TOKEN"],
    'database': os.environ["BOT_TOKEN"],
}


group_ID = {
    "consult_group_id": os.environ["CONSULT_GROUP_ID"],
    "auto_consult_id": os.environ["AUTO_GROUP_ID"],
    "audit_id": os.environ["AUDIT_GROUP_ID"],
    "all_consult_id": os.environ["ALL_CONSULT_ID"]
}