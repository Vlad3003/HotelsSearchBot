from telebot.handler_backends import State, StatesGroup
from datetime import date

class UserState(StatesGroup):
	"""
	Класс, реализующий состояние пользователя внутри сценария.
    Атрибуты заполняются постепенно во время опроса пользователя.

    Attributes:
    	date_str (str): дата ввода команды
    	command (str): команда, которую ввёл пользователь.
    	city_id (str): id города, в котором будет произведён поиск отелей.
    	cities (dict): подходящие по названию города, из которых пользователь выбирает нужный ему.
    	count_hotels (int): количество отелей.
    	need_photo (bool): нужны ли фотографии отеля.
    	count_photos (int): количество фотографий отеля.
    	date_in (date): дата заезда в отель.
    	date_out (date): дата выезда из отеля.
    	max_price (int): максимальная цена за ночь.
    	min_price (int): минимальная цена за ночь.
    	max_distance (int): максимальная дистанция до центра города.
	"""
	date_str = State()
	command = State()
	city_id = State()
	cities = State()
	count_hotels = State()
	need_photo = State()
	count_photos = State()
	date_in = State()
	date_out = State()
	max_price = State()
	min_price = State()
	max_distance = State()
