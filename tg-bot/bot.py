import logging
import random
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токен
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден! Создай файл .env с BOT_TOKEN=твой_токен")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

MOCK_MUSHROOMS = [
    {"name": "Белый гриб", "poisonous": False},
    {"name": "Мухомор красный", "poisonous": True},
    {"name": "Лисичка", "poisonous": False},
    {"name": "Бледная поганка", "poisonous": True},
    {"name": "Подберезовик", "poisonous": False},
    {"name": "Свинушка тонкая", "poisonous": True},
    {"name": "Опята", "poisonous": False},
]

async def start(update: Update, context):
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
    
    # Эмуляция работы модели
    await update.message.reply_text("🔍 Анализирую гриб...")
    
    mushroom = random.choice(MOCK_MUSHROOMS)
    toxicity = "⚠️ ЯДОВИТЫЙ! Ни в коем случае не ешь!" if mushroom["poisonous"] else "✅ Съедобный, но лучше проконсультироваться со специалистом"
    
    reply = f"🍄 *{mushroom['name']}*\n\n{toxicity}\n\n---\n_🧪 Режим тестирования модели. Скоро здесь будет настоящий ИИ!_"
    await update.message.reply_text(reply, parse_mode="Markdown")

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