from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data.config import BOT_TOKEN, LOG_PATH
from peewee import SqliteDatabase
from loguru import logger

storage = StateMemoryStorage()
bot = TeleBot(token=BOT_TOKEN, state_storage=storage)
db = SqliteDatabase("history.db")
logger.add(LOG_PATH, format="{time}, {level}, {message}",
		   level="DEBUG", rotation="1 week", compression="zip")
