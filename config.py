import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database import Database

load_dotenv()
BOT_TOKEN=os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv("ADMIN_ID")
BOT_ID = os.getenv('BOT_ID')
DB = os.getenv('DB')
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


# Создаём объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База данных
db = Database()