from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from loguru import logger

@bot.message_handler(commands=["help"])
@logger.catch
def bot_help(message: Message) -> None:
	"""
	Функция реагирует на команду 'help' и отправляет сообщение пользователю со списком доступных команд.
	:param message: сообщение Telegram
	:return: None
	"""
	commands = [f"/{command} - {description}"
				for command, description in DEFAULT_COMMANDS]

	text = "Список доступных команд:\n" + "\n".join(commands)
	bot.send_message(chat_id=message.chat.id, text=text)

	bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
