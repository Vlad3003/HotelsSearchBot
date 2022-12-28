from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict

def cities_list_keyboard(cities: Dict[str, str]) -> InlineKeyboardMarkup:
	"""
	Функция, которая создаёт клавиатуру со списком городов.
	:param cities: словарь с городами, где ключ - id этого города, а значение сам город.
	:type cities: dict
	:return: клавиатура со списком городов.
	:rtype: InlineKeyboardMarkup
	"""
	markup = InlineKeyboardMarkup()

	for city_id, city in cities.items():
		button = InlineKeyboardButton(text=city, callback_data=f"city_id={city_id}")
		markup.add(button)

	return markup
