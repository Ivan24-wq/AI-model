from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")

client = MongoClient(uri)

db = client["intelect"]
collection = db["Users"]

try:
    client.admin.command('ping')
    print("Успешное подключение MongoDb")
except Exception as ex:
    print(f"Сбой {ex}")