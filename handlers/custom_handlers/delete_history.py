from loader import bot
from telebot.types import Message
from database.db import delete_information
from keyboards.inline.history_keyboard import HistoryKeyboard
from loguru import logger

@bot.message_handler(commands=["delete_history"])
@logger.catch
def delete_history(message: Message) -> None:
	"""
	Функция реагирует на команду 'delete_history' и удаляет историю поиска отелей.
	:param message: сообщение Telegram
	:return: None
	"""
	user = (message.from_user.id, message.chat.id)

	delete_information(telegram_id=user[0], chat_id=user[1])

	bot.send_message(chat_id=message.chat.id, text="История поиска была очищена")

	if HistoryKeyboard.all_keyboards.get(user):
		message_id = HistoryKeyboard.all_keyboards[user].message_id
		HistoryKeyboard.all_keyboards[user] = None
		bot.delete_message(chat_id=message.chat.id, message_id=message_id)
