from loader import bot
from telebot.types import Message, CallbackQuery
from database.db import get_information
from database.models import User
from keyboards.inline.history_keyboard import HistoryKeyboard
from typing import List
from loguru import logger

@bot.message_handler(commands=["history"])
@logger.catch
def history(message: Message) -> None:
	"""
	Функция реагирует на команду 'history' и отображает историю поиска отелей.
	:param message: сообщение Telegram
	:return: None
	"""
	mes = bot.send_message(chat_id=message.chat.id, text="⏳")

	user = (message.from_user.id, message.chat.id)

	if HistoryKeyboard.all_keyboards.get(user):
		message_id = HistoryKeyboard.all_keyboards[user].message_id
		HistoryKeyboard.all_keyboards[user] = None
		bot.delete_message(chat_id=message.chat.id, message_id=message_id)

	conditions = [User.telegram_id == user[0], User.chat_id == user[1]]
	result = [(history.date, history.command) for history in get_information(conditions=conditions)]

	if result:
		HistoryKeyboard.all_keyboards[user] = HistoryKeyboard(dates=result, message_id=mes.message_id)
		markup = HistoryKeyboard.all_keyboards[user].dates_keyboard(start_index=0)

		bot.edit_message_text(text="Выберите запрос:", chat_id=message.chat.id,
							  reply_markup=markup, message_id=mes.message_id)

	else:
		bot.edit_message_text(text="История поиска пуста или очищена",
							  chat_id=message.chat.id,
							  message_id=mes.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("**"))
@logger.catch
def history_keyboard_callback(call: CallbackQuery):
	"""
	Функция, которая реагирует на нажатие кнопки клавиатуры 'HistoryKeyboard'
	:return: None
	"""
	user = (call.from_user.id, call.message.chat.id)

	if call.data.startswith("**hotels_keyboard&"):
		date, command = call.data.split("&")[1:]
		conditions = [User.telegram_id == user[0], User.chat_id == user[1],
					  User.date == date, User.command == command]

		result: List[User] = get_information(conditions=conditions)

		if "&&" in result[0].result:
			hotels = result[0].result.split("&&")

		elif result[0].result:
			hotels = [result[0].result]

		else:
			hotels = []

		HistoryKeyboard.all_keyboards[user].request_parameters = result[0].request_parameters
		HistoryKeyboard.all_keyboards[user].hotels = hotels

	if call.data.startswith("**hotels_keyboard"):
		if call.data.startswith("**hotels_keyboard:"):
			start_index = int(call.data.split(":")[1])
			markup = HistoryKeyboard.all_keyboards[user].hotels_keyboard(start_index=start_index)

		else:
			markup = HistoryKeyboard.all_keyboards[user].hotels_keyboard(start_index=0)

		text = HistoryKeyboard.all_keyboards[user].request_parameters

		if len(HistoryKeyboard.all_keyboards[user].hotels) > 0:
			text += "\n\n<b>Выберите отель:</b>"

		bot.edit_message_text(text=text,
							  chat_id=call.message.chat.id,
							  reply_markup=markup,
							  message_id=call.message.message_id,
							  parse_mode="HTML")

	elif call.data.endswith("_page"):
		if call.data.startswith("**dates_page"):
			markup = HistoryKeyboard.all_keyboards[user].dates_page_keyboard()

		else:
			markup = HistoryKeyboard.all_keyboards[user].hotels_page_keyboard()

		bot.edit_message_text(text="Выберите страницу:",
							  chat_id=call.message.chat.id,
							  reply_markup=markup,
							  message_id=call.message.message_id)

	elif call.data.startswith("**dates_keyboard:"):
		start_index = int(call.data.split(":")[1])

		markup = HistoryKeyboard.all_keyboards[user].dates_keyboard(start_index=start_index)

		bot.edit_message_text(text="Выберите запрос:",
							  chat_id=call.message.chat.id,
							  reply_markup=markup,
							  message_id=call.message.message_id)

	elif call.data.startswith("**hotel_info:"):
		i_hotel = int(call.data.split(":")[1])

		text, markup = HistoryKeyboard.all_keyboards[user].hotel_info(i_hotel=i_hotel)

		bot.edit_message_text(text=text,
							  chat_id=call.message.chat.id,
							  reply_markup=markup,
							  message_id=call.message.message_id,
							  parse_mode="HTML",
							  disable_web_page_preview=True)
