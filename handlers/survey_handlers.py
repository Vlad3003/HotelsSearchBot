from loader import bot
from database.db import save_information
from states.hotels_search_information import UserState
from utils.getting_data import get_city_id, get_hotels, get_hotel_info_str, get_price_str
from keyboards.inline.cities_list import cities_list_keyboard
from keyboards.inline.yes_or_no import yes_or_no_keyboard
from keyboards.inline.calendar_keyboard import CalendarKeyboard
from keyboards.inline.history_keyboard import HistoryKeyboard
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto
from datetime import date, timedelta
from loguru import logger

@bot.message_handler(state=UserState.city_id)
@logger.catch
def get_city(message: Message) -> None:
	"""
	Функция, которая получает от пользователя город и предлагает выбрать подходящий вариант из списка городов.
	:param message: сообщение Telegram
	:return: None
	"""
	mes = bot.send_message(chat_id=message.chat.id, text="⏳")
	result = get_city_id(city=message.text)

	if result:
		markup = cities_list_keyboard(cities=result)
		bot.edit_message_text(text="Выберите подходящий вариант из списка:",
							  chat_id=message.chat.id,
							  message_id=mes.message_id,
							  reply_markup=markup)
		with bot.retrieve_data(user_id=message.from_user.id,
							   chat_id=message.chat.id) as data:
			data["cities"] = result

		bot.set_state(user_id=message.from_user.id,
					  state=UserState.max_price,
					  chat_id=message.chat.id)
	else:
		bot.edit_message_text(text="Произошла ошибка. Попробуйте ввести другой город!",
							  chat_id=message.chat.id, message_id=mes.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("city_id="))
@logger.catch
def set_city_id(call: CallbackQuery) -> None:
	"""
	Функция, которая реагирует на нажатие кнопки с городом. Сохраняет выбранный город и
	предлагает ввести количество отелей.
	:return: None
	"""
	city_id = call.data.split("=")[1]

	with bot.retrieve_data(user_id=call.from_user.id,
						   chat_id=call.message.chat.id) as data:
		data["city_id"] = city_id
		city = data["cities"][city_id]

		bot.edit_message_text(text=f"Вы выбрали: {city}",
							  chat_id=call.message.chat.id,
							  message_id=call.message.message_id)

	bot.send_message(chat_id=call.message.chat.id, text="Введите количество отелей")

	bot.set_state(user_id=call.from_user.id,
				  state=UserState.count_hotels,
				  chat_id=call.message.chat.id)

@bot.message_handler(state=UserState.count_hotels)
@logger.catch
def get_count_hotels(message: Message) -> None:
	"""
	Функция, которая получает от пользователя количество отелей.
	:param message: сообщение Telegram
	:return: None
	"""
	if message.text.isdigit() and (0 < int(message.text) < 16):
		with bot.retrieve_data(user_id=message.from_user.id,
							   chat_id=message.chat.id) as data:
			data["count_hotels"] = int(message.text)

			markup = yes_or_no_keyboard()
			bot.send_message(chat_id=message.chat.id,
							 text="Нужны фотографии?",
							 reply_markup=markup)

			bot.set_state(user_id=message.from_user.id,
						  state=UserState.need_photo,
						  chat_id=message.chat.id)
	else:
		bot.send_message(chat_id=message.chat.id,
						 text="Произошла ошибка.\nВведите <b>число от 1 до 15!</b>",
						 parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data in ("yes", "no"),
							state=UserState.need_photo)
@logger.catch
def set_count_photos(call: CallbackQuery) -> None:
	"""
	Функция, которая реагирует на нажатие кнопки. Если пользователю нужны фотографии отеля,
	то пользователю будет предложено ввести количество фотографий. Иначе пользователю будет предложено
	выбрать дату заезда.
	:return: None
	"""
	if call.data == "no":
		with bot.retrieve_data(user_id=call.from_user.id,
							   chat_id=call.message.chat.id) as data:
			data["count_photos"] = 0
			data["need_photo"] = False
			data["date_in"] = CalendarKeyboard()

			markup = data["date_in"].month()

			bot.edit_message_text(text="Выберите дату заезда:",
								  chat_id=call.message.chat.id,
								  message_id=call.message.message_id,
								  reply_markup=markup)

			bot.set_state(user_id=call.from_user.id,
						  state=UserState.date_in,
						  chat_id=call.message.chat.id)
	else:
		bot.edit_message_text(text="Введите количество фотографий",
							  chat_id=call.message.chat.id,
							  message_id=call.message.message_id)

		bot.set_state(user_id=call.from_user.id,
					  state=UserState.count_photos,
					  chat_id=call.message.chat.id)

@bot.message_handler(state=UserState.count_photos)
@logger.catch
def get_count_photos(message: Message) -> None:
	"""
	Функция, которая получает от пользователя количество фотографий отеля и предлагает выбрать дату заезда.
	:param message: сообщение Telegram
	:return: None
	"""
	if message.text.isdigit() and (0 < int(message.text) < 11):
		with bot.retrieve_data(user_id=message.from_user.id,
							   chat_id=message.chat.id) as data:

			data["count_photos"] = int(message.text)
			data["need_photo"] = True
			data["date_in"] = CalendarKeyboard()

			markup = data["date_in"].month()

			bot.send_message(chat_id=message.chat.id,
							 text="Выберите дату заезда:",
							 reply_markup=markup)

			bot.set_state(user_id=message.from_user.id,
						  state=UserState.date_in,
						  chat_id=message.chat.id)
	else:
		bot.send_message(chat_id=message.chat.id,
						 text="Произошла ошибка.\nВведите <b>число от 1 до 10!</b>",
						 parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("__"))
@logger.catch
def calendar_callback(call: CallbackQuery):
	"""
	Функция, которая реагирует на нажатие кнопки в календаре.
	:return: None
	"""
	with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
		if bot.get_state(user_id=call.from_user.id,
						 chat_id=call.message.chat.id) == "UserState:date_in":

			keyboard = data["date_in"]

		elif bot.get_state(user_id=call.from_user.id,
						   chat_id=call.message.chat.id) == "UserState:date_out":

			keyboard = data["date_out"]

	command, data = call.data.split(":")
	arguments = list(map(int, data.split()))

	if command == "__month":
		markup = keyboard.month(*arguments)

	elif command == "__months":
		markup = keyboard.months(*arguments)

	elif command == "__years":
		markup = keyboard.years(*arguments)

	else:
		markup = InlineKeyboardMarkup()

	bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_date:"))
@logger.catch
def set_date(call: CallbackQuery) -> None:
	"""
	Функция, которая реагирует на нажатие кнопки выбора даты.
	:return: None
	"""
	day, month, year = map(int, call.data.split(":")[1].split())
	date_out_received = False

	with bot.retrieve_data(user_id=call.from_user.id,
						   chat_id=call.message.chat.id) as data:

		if bot.get_state(user_id=call.from_user.id,
						 chat_id=call.message.chat.id) == "UserState:date_in":

			data["date_in"] = date(year=year, month=month, day=day)
			selected_date = data["date_in"].strftime("%d.%m.%Y")

			bot.edit_message_text(text=f"📆 Дата заезда: {selected_date}",
								  chat_id=call.message.chat.id,
								  message_id=call.message.message_id)

			bot.set_state(user_id=call.from_user.id,
						  state=UserState.date_out,
						  chat_id=call.message.chat.id)

			data["date_out"] = CalendarKeyboard(min_date=data["date_in"] + timedelta(days=1))
			markup = data["date_out"].month()

			bot.send_message(chat_id=call.message.chat.id,
							 text="Выберите дату выезда:",
							 reply_markup=markup)

		elif bot.get_state(user_id=call.from_user.id,
						   chat_id=call.message.chat.id) == "UserState:date_out":

			data["date_out"] = date(year=year, month=month, day=day)
			selected_date = data["date_out"].strftime("%d.%m.%Y")

			bot.edit_message_text(text=f"📆 Дата выезда: {selected_date}",
								  chat_id=call.message.chat.id,
								  message_id=call.message.message_id)

			date_out_received = True

	if date_out_received:
		if data["command"] in ("lowprice", "highprice"):
			hotels_list(user_id=call.from_user.id,
						chat_id=call.message.chat.id,
						name=call.from_user.full_name,
						username=call.from_user.username)

		elif data["command"] == "bestdeal":
			bot.send_message(chat_id=call.message.chat.id,
							 text="Введите минимальную и максимальную\nцену за"
								  " 1 ночь в $ через пробел.\nНапример: 100 150")

			bot.set_state(user_id=call.from_user.id,
						  state=UserState.min_price,
						  chat_id=call.message.chat.id)

@bot.message_handler(state=UserState.min_price)
@logger.catch
def get_price_range(message: Message) -> None:
	"""
	Функция, которая получает от пользователя минимальную и максимальную цену за 1 ночь.
	:param message: сообщение Telegram
	:return: None
	"""
	try:
		min_price, max_price = map(int, message.text.split())

		if min_price > max_price:
			min_price, max_price = max_price, min_price
			bot.send_message(chat_id=message.chat.id,
							 text="Вы перепутали минимальную цену с "
								  "максимальной! Но я всё сделал за вас.")

		if min_price == max_price:
			bot.send_message(chat_id=message.chat.id,
							 text="Минимальная цена не должна быть равна"
								  "\nмаксимальной! Попробуйте ввести ещё раз!")
			return None

		if min_price <= 0:
			bot.send_message(chat_id=message.chat.id,
							 text="Минимальная цена должна\nбыть <b>больше ноля!</b>",
							 parse_mode="HTML")
			return None

		with bot.retrieve_data(user_id=message.from_user.id,
							   chat_id=message.chat.id) as data:

			data["min_price"] = min_price
			data["max_price"] = max_price

		bot.set_state(user_id=message.from_user.id,
					  state=UserState.max_distance,
					  chat_id=message.chat.id)

		bot.send_message(chat_id=message.chat.id,
						 text="Введите максимальное расстояние"
							  "\nв км до центра города")

	except ValueError:
		bot.send_message(chat_id=message.chat.id,
						 text="Произошла ошибка. Вам нужно\nввести <b>два</b> числа <b>через пробел!</b>",
						 parse_mode="HTML")

@bot.message_handler(state=UserState.max_distance)
@logger.catch
def get_max_distance(message: Message) -> None:
	"""
	Функция, которая получает от пользователя максимальное расстояние от центра города.
	:param message: сообщение Telegram
	:return: None
	"""
	try:
		max_distance = int(message.text)

		if max_distance < 0:
			raise ValueError("Введённое число меньше нуля")

		if max_distance == 0:
			bot.send_message(chat_id=message.chat.id,
							 text="Расстояние должно быть <b>больше ноля!</b>",
							 parse_mode="HTML")
			return None

		with bot.retrieve_data(user_id=message.from_user.id,
							   chat_id=message.chat.id) as data:

			data["max_distance"] = max_distance

		hotels_list(user_id=message.from_user.id,
					chat_id=message.chat.id,
					name=message.from_user.full_name,
					username=message.from_user.username)

	except ValueError:
		bot.send_message(chat_id=message.chat.id,
						 text="Произошла ошибка. Вам нужно ввести \n<b>целое положительное</b> число!",
						 parse_mode="HTML")

@logger.catch
def hotels_list(user_id: str, chat_id: str, name: str, username: str) -> None:
	"""
	Функция, которая отправляет пользователю информацию об найденных отелях.
	:param user_id: id пользователя
	:param chat_id: чат id
	:param name: имя
	:param username: имя пользователя
	:return: None
	"""
	sorting = {
		"lowprice": "PRICE_LOW_TO_HIGH",
		"highprice": "PRICE_HIGHEST_FIRST",
		"bestdeal": "DISTANCE"
	}

	count_hotels = 0
	result = {}
	hotels = ''

	mes = bot.send_message(chat_id=chat_id, text="⏳")

	with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
		result["date"] = data["date_str"]
		result["command"] = data["command"]

		if data["command"] == "bestdeal":
			params = {
				"min_price": data["min_price"],
				"max_price": data["max_price"]
			}

		else:
			params = None

		for hotel_data in get_hotels(command=data["command"],
									 region_Id=data["city_id"],
									 check_In_Date=data["date_in"],
									 check_Out_Date=data["date_out"],
									 sort=sorting[data["command"]],
									 count_photos=data["count_photos"],
									 count_hotels=data["count_hotels"],
									 params=params):
			if hotel_data is None:
				bot.edit_message_text(text="Произошла ошибка. Попробуйте ещё раз!"
										   "\nИли попробуйте ввести другой город!",
									  chat_id=chat_id, message_id=mes.message_id)

				bot.set_state(user_id=user_id,
							  state=UserState.city_id,
							  chat_id=chat_id)
				return None

			else:
				if data["command"] == "bestdeal":
					if count_hotels == data["count_hotels"]:
						break

					if not(data["min_price"] <= hotel_data["price"] <= data["max_price"]):
						continue

					distance = float(hotel_data["distance"].split()[0])

					if distance > data["max_distance"]:
						break

				count_hotels += 1

				count_nights = data["date_out"] - data["date_in"]
				text = get_hotel_info_str(data=hotel_data, count_nights=count_nights.days)

				if count_hotels == 1:
					hotels += text

				else:
					hotels += '&&'
					hotels += text

				if len(hotel_data["photos"]) == 0:
					bot.send_message(chat_id=chat_id, text=text,
									 parse_mode="HTML", disable_web_page_preview=True)

				else:
					photos = [InputMediaPhoto(hotel_data['photos'][i_link], caption=text, parse_mode="HTML")
								if i_link == 0
								else InputMediaPhoto(hotel_data['photos'][i_link], caption='')
							  for i_link in range(len(hotel_data['photos']))]

					bot.send_media_group(chat_id=chat_id, media=photos)

				bot.send_location(chat_id=chat_id,
								  latitude=hotel_data["latitude"],
								  longitude=hotel_data["longitude"])

		if count_hotels == data["count_hotels"]:
			bot.send_message(chat_id=chat_id, text="🔍 Поиск завершён")

		else:
			text = f"По вашему запросу было\nнайдено {count_hotels} отелей из {data['count_hotels']}"

			if count_hotels == 1:
				text = text.replace("было\nнайдено", "был\nнайден", 1)
				text = text.replace("отелей", "отель", 1)

			elif count_hotels in (2, 3, 4):
				text = text.replace("отелей", "отеля", 1)

			bot.send_message(chat_id=chat_id, text=text)

		date_in = data["date_in"].strftime("%d.%m.%Y")
		date_out = data["date_out"].strftime("%d.%m.%Y")

		request_parameters = "<b>Параметры запроса:</b>\n\n" \
							 f"<b>Команда:</b> /{data['command']}\n" \
							 f"<b>Дата и время ввода команды:</b> {data['date_str']}\n" \
							 f"<b>Город:</b> {data['cities'][data['city_id']]}\n" \
							 f"<b>Количество отелей:</b> {data['count_hotels']}\n" \
							 f"<b>Количество фотографий:</b> {data['count_photos']}\n" \
							 f"<b>Дата заезда:</b> {date_in}\n" \
							 f"<b>Дата выезда:</b> {date_out}"

		if data["command"] == "bestdeal":
			min_price = get_price_str(str(data["min_price"]))
			max_price = get_price_str(str(data["max_price"]))

			request_parameters += f"\n<b>Минимальная цена за 1 ночь:</b> {min_price}\n" \
								  f"<b>Максимальная цена за 1 ночь:</b> {max_price}\n" \
								  f"<b>Максимальное расстояние до центра города:</b> {data['max_distance']} км\n" \
								  f"<b>Найдено отелей:</b> {count_hotels} из {data['count_hotels']}"
	user = (user_id, chat_id)

	if HistoryKeyboard.all_keyboards.get(user):
		message_id = HistoryKeyboard.all_keyboards[user].message_id
		HistoryKeyboard.all_keyboards[user] = None

		bot.delete_message(chat_id=chat_id, message_id=message_id)

	bot.delete_message(chat_id=chat_id, message_id=mes.message_id)
	bot.delete_state(user_id=user_id, chat_id=chat_id)

	result["request_parameters"] = request_parameters
	result["result"] = hotels
	result["telegram_id"] = user_id
	result["chat_id"] = chat_id
	result["name"] = name
	result["username"] = username

	save_information(data=result)
