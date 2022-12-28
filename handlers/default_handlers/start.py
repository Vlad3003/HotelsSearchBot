from telebot.types import Message
from loader import bot
from loguru import logger

@bot.message_handler(commands=["start", "hello-world"])
@logger.catch
def bot_start(message: Message) -> None:
	"""
	Функция реагирует на команды 'start', 'hello-world' и отправляет приветственное сообщение
	:param message: сообщение Telegram
	:return: None
	"""
	text = f"Привет {message.from_user.full_name}! Предлагаю воспользоваться командой /help"

	bot.send_message(chat_id=message.chat.id, text=text)

	bot.delete_state(user_id=message.from_user.id, chat_id=message.chat.id)
