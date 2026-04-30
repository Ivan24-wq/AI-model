from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from routers import pages, auth
from routers.database import client
from routers.database import collection
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend"
)

app.include_router(pages.router)
app.include_router(auth.router)

#Подключение Бд
@app.get("/connect-mongo")
def connect_mongo():
    try:
        client.admin.command('ping')
        print("Успешное подключение MongoDb")
    except Exception as ex:
        print(f"Сбой {ex}")

@app.on_event("startup")
async def startup():
    collection.create_index("expires_at", expireAfterSeconds = 0)