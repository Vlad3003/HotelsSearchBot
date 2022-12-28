from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil
from typing import Tuple, Optional, List, Dict
import re
from datetime import date

class HistoryKeyboard:
	"""
	Класс клавиатура Telegram для команды 'history'.

	Args:
		dates (list): список дат с командами
		message_id (int): id сообщения отправленного с этой клавиатурой

	Attributes:
		all_keyboards (dict): словарь с инстансами этого класса
		request_parameters (str): параметры запроса
		hotels (list): список отелей
		dates_start_index (int): номер индекса даты, которая будет на первой кнопке,
		при нажатии кнопки назад
	"""

	all_keyboards: Dict[Tuple[int, int], 'HistoryKeyboard'] = {}

	def __init__(self, dates: list, message_id: int) -> None:
		self.dates = dates
		self.message_id = message_id
		self.request_parameters: Optional[str] = None
		self.hotels: Optional[List[str]] = None
		self.dates_start_index = 0

	def dates_keyboard(self, start_index: int) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру с датами и командами.
		:param start_index: номер индекса даты, которая будет на первой кнопке.
		:type start_index: int
		"""
		markup = InlineKeyboardMarkup()

		self.dates_start_index = start_index

		for i_date in range(start_index, len(self.dates)):
			_date, command = self.dates[i_date]
			button = InlineKeyboardButton(text=f"{_date} {command}",
										  callback_data=f"**hotels_keyboard&{_date}&{command}")
			markup.add(button)

			if i_date == start_index + 4:
				break

		page_num = start_index // 5 + 1

		prev_button_text, prev_button_date = self.__previous_page_dates(page_num=page_num)
		next_button_text, next_button_date = self.__next_page_dates(page_num=page_num)

		prev_button = InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_date)
		middle_button = InlineKeyboardButton(text=f"{page_num}", callback_data=f'**dates_page')
		next_button = InlineKeyboardButton(text=next_button_text, callback_data=next_button_date)

		markup.add(prev_button, middle_button, next_button)

		return markup

	def dates_page_keyboard(self) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру - 'номера страниц дат'.
		"""
		markup = InlineKeyboardMarkup()

		buttons = []

		for page_num in range(1, ceil(len(self.dates) / 5) + 1):
			start_index = (page_num - 1) * 5
			button = InlineKeyboardButton(text=page_num, callback_data=f"**dates_keyboard:{start_index}")

			buttons.append(button)

			if len(buttons) == 3:
				markup.add(*buttons)
				buttons = []

		if buttons:
			markup.add(*buttons)

		return markup

	@classmethod
	def __previous_page_dates(cls, page_num: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить предыдущую страницу с датами.
		:param page_num: номер страницы.
		:type page_num: int
		"""
		if page_num - 1 > 0:
			start_index = (page_num - 2) * 5

			return "<", f"**dates_keyboard:{start_index}"
		return " ", f"None1"

	def __next_page_dates(self, page_num: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить следующую страницу с датами.
		:param page_num: номер страницы.
		:type page_num: int
		"""
		if len(self.dates) > page_num * 5:
			start_index = page_num * 5

			return ">", f"**dates_keyboard:{start_index}"
		return " ", "None2"

	def hotels_keyboard(self, start_index: int) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру - 'список отелей'.
		:param start_index: номер индекса отеля, который будет на первой кнопке.
		:type start_index: int
		"""
		markup = InlineKeyboardMarkup()
		delete_dates = None

		for i_hotel in range(start_index, len(self.hotels)):
			name = re.findall(r"🏠 <b>(.+)</b>", self.hotels[i_hotel])[0]

			if delete_dates is None:
				date_in_str = re.findall(r"chkin=(.*)&chkout", self.hotels[i_hotel])

				if date_in_str:
					year, month, day = map(int, date_in_str[0].split("-"))
					date_in = date(year=year + 1, month=month, day=day)

					now = date.today()

					if all([date_in.year >= now.year, date_in.month >= now.month, date_in.day >= now.day]):
						delete_dates = False

					else:
						delete_dates = True

			if delete_dates:
				self.hotels[i_hotel] = re.sub(r"/\?.*a1", "", self.hotels[i_hotel])

			button = InlineKeyboardButton(text=f"{i_hotel + 1}. {name}", callback_data=f"**hotel_info:{i_hotel}")
			markup.add(button)

			if i_hotel == start_index + 4:
				break

		if len(self.hotels) > 0:
			page_num = start_index // 5 + 1

			prev_button_text, prev_button_date = self.__previous_page_hotels(page_num=page_num)
			next_button_text, next_button_date = self.__next_page_hotels(page_num=page_num)

			prev_button = InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_date)
			middle_button = InlineKeyboardButton(text=f"{page_num}", callback_data=f'**hotels_page')
			next_button = InlineKeyboardButton(text=next_button_text, callback_data=next_button_date)

			markup.add(prev_button, middle_button, next_button)

		back_button = InlineKeyboardButton(text="Назад", callback_data=f"**dates_keyboard:{self.dates_start_index}")

		markup.add(back_button)

		return markup

	@classmethod
	def __previous_page_hotels(cls, page_num: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить предыдущую страницу с отелями.
		:param page_num: номер страницы.
		:type page_num: int
		"""
		if page_num - 1 > 0:
			start_index = (page_num - 2) * 5

			return "<", f"**hotels_keyboard:{start_index}"
		return " ", f"None1"

	def __next_page_hotels(self, page_num: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить следующую страницу с отелями.
		:param page_num: номер страницы.
		:type page_num: int
		"""
		if len(self.hotels) > page_num * 5:
			start_index = page_num * 5

			return ">", f"**hotels_keyboard:{start_index}"
		return " ", "None2"

	def hotels_page_keyboard(self) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру - 'номера страниц отелей'.
		"""
		markup = InlineKeyboardMarkup()

		buttons = []

		for page_num in range(1, ceil(len(self.hotels) / 5) + 1):
			start_index = (page_num - 1) * 5
			button = InlineKeyboardButton(text=page_num, callback_data=f"**hotels_keyboard:{start_index}")

			buttons.append(button)

			if len(buttons) == 3:
				markup.add(*buttons)
				buttons = []

		if buttons:
			markup.add(*buttons)

		return markup

	def hotel_info(self, i_hotel: int) -> Tuple[str, InlineKeyboardMarkup]:
		"""
		Функция, которая возвращает описание отеля и клавиатуру для перемещения между отелями.
		:param i_hotel: индекс отеля.
		:type i_hotel: int
		"""
		markup = InlineKeyboardMarkup()

		text = self.hotels[i_hotel]

		prev_button_text, prev_button_date = self.__previous_hotel(i_hotel=i_hotel)
		next_button_text, next_button_date = self.__next_hotel(i_hotel=i_hotel)

		start_index = i_hotel // 5 * 5

		prev_button = InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_date)
		middle_button = InlineKeyboardButton(text=f"{i_hotel + 1}", callback_data=f'**hotels_keyboard:{start_index}')
		next_button = InlineKeyboardButton(text=next_button_text, callback_data=next_button_date)

		markup.add(prev_button, middle_button, next_button)

		return text, markup

	@classmethod
	def __previous_hotel(cls, i_hotel: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить предыдущий отель.
		:param i_hotel: индекс отеля.
		:type i_hotel: int
		"""
		if i_hotel - 1 >= 0:

			return "<", f"**hotel_info:{i_hotel - 1}"
		return " ", f"None1"

	def __next_hotel(self, i_hotel: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить следующий отель.
		:param i_hotel: индекс отеля.
		:type i_hotel: int
		"""
		if len(self.hotels) > i_hotel + 1:

			return ">", f"**hotel_info:{i_hotel + 1}"
		return " ", "None2"
