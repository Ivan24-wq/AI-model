import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import httpx

# Токен
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")
API_URL = os.getenv("API_URL")

if not TOKEN:
    raise ValueError("Токен не найден! Создай файл .env с BOT_TOKEN=твой_токен")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)



async def start(update: Update, context):
    #Запрос на backend
    user = update.effective_user
    
    payload = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username
    }
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/telegram/register",
                json=payload,
                headers=headers
            )
        print(response.json())
    except Exception as ex:
        print(f"ошибка на стороне сервера! {ex}")
    
    await update.message.reply_text(
        "🍄 Привет! Я бот для распознавания грибов Крыма.\n\n"
        "Отправь мне фото гриба, и я скажу, что это за вид и ядовит ли он.\n"
        "Узнать подробности — /info"
    )

async def info(update: Update, context):
    info_text = """
📋 *О проекте «MycoAI»*

Миссия: Создать удобное приложение для определения съедобности грибов

🤖 *Как работает бот:*  
1. Вы отправляете фото гриба  
2. ИИ анализирует изображение  
3. Бот сообщает название и статус (съедобный/ядовитый)

👥 *Наша команда:*  
• Воронин Иван
• Покидько Никита
• Битюков Кирилл
• Рогожников Кирилл

🍄 *Какие грибы умеем распознавать:*  
• Белый гриб (съедобный)  
• Лисичка (съедобная)  
• Подберезовик (съедобный)  
• Мухомор (ядовитый)  
• Бледная поганка (ядовитая)  
• Свинушка (ядовитая)  
• Опята (съедобные)

---
*Команды бота:*  
/start — начать работу  
/info — информация о проекте
"""
    await update.message.reply_text(info_text, parse_mode="Markdown")

async def handle_photo(update: Update, context):
    # Имитация загрузки фото (пока просто логируем)
    photo_file = await update.message.photo[-1].get_file()
    logging.info(f"Получено фото от {update.message.from_user.first_name}, файл: {photo_file.file_id}")
    
    try:
        # Получаем фото
        photo = update.message.photo[-1]

        # Telegram file
        photo_file = await photo.get_file()

        # Скачиваем bytes
        photo_bytes = bytes(
            await photo_file.download_as_bytearray()
        ) 

        headers = {
            "X-API-Key": API_KEY
        }

        files = {
            "file": (
                "mushroom.jpg",
                photo_bytes,
                "image/jpeg"
            )
        }
        
        #Отправка на бэк
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE}/api/predict",
                headers=headers,
                files=files,
                data = {
                    "model_type": "improved"
                }
            )
        
        result = response.json()

        mushroom_class = result["Класс"]
        probability = result["Вероятность"]

        # Ответ пользователю
        if mushroom_class == "Ядовитый":
            status = "⚠️ ЯДОВИТЫЙ!"
        else:
            status = "✅ Съедобный"

        reply = (
            f"🍄 Результат анализа:\n\n"
            f"{status}\n\n"
            f"🎯 Вероятность: {probability:.2%}"
        )

        await update.message.reply_text(reply)
    except Exception as ex:
        logging.exception(ex)
        
        await update.message.reply_text("Ошибка анализа изображения!")

async def unknown(update: Update, context):
    await update.message.reply_text("❌ Пожалуйста, отправь именно фото гриба. Команды: /start или /info")

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    
    # Обработка фото
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Всё остальное (текст, стикеры и т.д.)
    app.add_handler(MessageHandler(filters.ALL, unknown))
    
    print("🤖 Бот запущен! Команды: /start, /info")
    print("Ожидаю фотографии грибов...")
    app.run_polling()

if __name__ == "__main__":
    main()