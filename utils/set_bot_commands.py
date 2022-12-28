from telebot import TeleBot, types
from config_data.config import DEFAULT_COMMANDS

def set_default_commands(bot: TeleBot) -> None:
	"""
	Функция, которая устанавливает команды бота
	:param bot: бот Telegram
	:type bot: TeleBot
	:return: None
	"""
	bot.set_my_commands(
		[types.BotCommand(*i_line) for i_line in DEFAULT_COMMANDS]
	)
