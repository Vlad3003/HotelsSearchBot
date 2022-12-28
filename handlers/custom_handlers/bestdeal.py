from loader import bot
from states.hotels_search_information import UserState
from telebot.types import Message
from datetime import datetime
from loguru import logger

@bot.message_handler(commands=["bestdeal"])
@logger.catch
def best_deal(message: Message) -> None:
	"""
	Функция реагирует на команду 'bestdeal' и предлагает ввести город для поиска отелей.
	:param message: сообщение Telegram
	:return: None
	"""
	bot.send_message(chat_id=message.chat.id, text="Введите город для поиска")

	bot.set_state(user_id=message.from_user.id,
				  state=UserState.city_id,
				  chat_id=message.chat.id)

	with bot.retrieve_data(user_id=message.from_user.id,
						   chat_id=message.chat.id) as data:
		data["command"] = "bestdeal"
		now = datetime.now().strftime("%d.%m.%Y %H:%M")
		data["date_str"] = now
