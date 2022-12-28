from loader import bot
from telebot.types import Message
from loguru import logger

@bot.message_handler(func=lambda message: True)
@logger.catch
def echo(message: Message) -> None:
	"""
	Функция, реагирующая на все сообщения от пользователя.
	:param message: сообщение Telegram
	:return: None
	"""
	if message.text.lower() == "привет":
		bot.send_message(chat_id=message.chat.id, text=f"Привет {message.from_user.full_name}!")

	else:
		bot.send_message(chat_id=message.chat.id, text="Я вас не понимаю.\nВоспользуйтесь командой /help.")
