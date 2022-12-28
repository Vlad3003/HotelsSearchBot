from loader import bot
from database.db import create_db
from telebot.custom_filters import StateFilter
import handlers
from utils.set_bot_commands import set_default_commands
from loguru import logger

@logger.catch
def main() -> None:
	"""
	Функция, которая запускает бота
	:return: None
	"""
	bot.add_custom_filter(StateFilter(bot=bot))
	set_default_commands(bot=bot)
	create_db()
	bot.infinity_polling()

if __name__ == "__main__":
	main()
