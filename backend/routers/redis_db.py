import redis
from dotenv import load_dotenv
import os

load_dotenv()

redis = redis.Redis(
    host='redis-15635.c321.us-east-1-2.ec2.cloud.redislabs.com',
    port=15635,
    decode_responses=True,
    username="default",
    password= os.getenv("REDIS_PASSWORD"),
)

try:
    redis.ping()
    print("Redis успешно подключилась!")
except Exception as ex:
    print("Ошибка подключения к Redis: ", ex)