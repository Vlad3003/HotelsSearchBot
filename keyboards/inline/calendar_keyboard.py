from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from calendar import monthcalendar
from datetime import date
from typing import Optional, Tuple

class CalendarKeyboard:
	"""
	Класс клавиатура календарь для Telegram.

	__month: словарь с месяцами, где ключ - это номер месяца, а значение - сам месяц.

	Args:
		min_date (date): минимальная дата, которую можно будет выбрать в календаре,
		по умолчанию min_date равен сегодняшней дате.

	Attributes:
		max_date (date): максимальная дата, которую можно будет выбрать в календаре,
		по умолчанию max_date равен 31 Декабря следующего года.
	"""
	__months = {
		1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
		5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
		9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
	}

	def __init__(self, min_date: date = date.today()) -> None:
		self.min_date = min_date
		self.max_date = date(year=date.today().year + 1, month=12, day=31)

	def month(self, year: Optional[int] = None, month: Optional[int] = None) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру календарь на указанный месяц.
		:param year: год.
		:param month: месяц.
		:return: клавиатура календарь на указанный месяц.
		:rtype: InlineKeyboardMarkup
		"""
		if year is None:
			year = self.min_date.year

		if month is None:
			month = self.min_date.month

		markup = InlineKeyboardMarkup(row_width=7)
		week_days = []

		for day in "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс":
			button = InlineKeyboardButton(text=day, callback_data=day)
			week_days.append(button)

		markup.add(*week_days)

		i_day = 0

		for week in monthcalendar(year=year, month=month):
			buttons = []

			for day in week:
				if day == 0:
					button = InlineKeyboardButton(text=" ", callback_data=f"empty_button:{i_day}")
					i_day += 1

				elif all([self.min_date.month == month, self.min_date.year == year, day < self.min_date.day]):
					button = InlineKeyboardButton(text=" ", callback_data=f"wrong_date:{year} {day}")

				else:
					button = InlineKeyboardButton(text=day, callback_data=f"set_date:{day} {month} {year}")

				buttons.append(button)

			markup.add(*buttons)

		prev_button_sym, prev_button_data = self.__last_month(year=year, month=month)
		next_button_sym, next_button_data = self.__next_month(year=year, month=month)

		prev_button = InlineKeyboardButton(text=prev_button_sym, callback_data=prev_button_data)
		middle_button = InlineKeyboardButton(text=f"{self.__months[month][:3]} {year}", callback_data=f'__months:{year}')
		next_button = InlineKeyboardButton(text=next_button_sym, callback_data=next_button_data)

		markup.add(prev_button, middle_button, next_button)

		return markup

	def __last_month(self, year: int, month: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить предыдущий месяц. Если можно, то указывает номер
		предыдущего месяца.
		:param year: год.
		:type year: int
		:param month: месяц.
		:type month: int
		:return: text_button, callback_data_button
		:rtype: tuple
		"""
		if self.min_date.month == month and self.min_date.year == year:
			return " ", f"None:{month}"

		if month - 1 == 0:
			return "<", f"__month:{year - 1} 12"

		return "<", f"__month:{year} {month - 1}"

	def __next_month(self, year: int, month: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить следующий месяц. Если можно, то указывает номер
		следующего месяца.
		:param year: год.
		:type year: int
		:param month: месяц.
		:type month: int
		:return: text_button, callback_data_button
		:rtype: tuple
		"""
		if month == 12 and self.max_date.year == year:
			return " ", f"None:{month}"

		if month + 1 == 13:
			return ">", f"__month:{year + 1} 1"

		return ">", f"__month:{year} {month + 1}"

	def months(self, year: int) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру со списком месяцев.
		:param year: год.
		:type year: int
		:return: клавиатура со списком месяцев.
		:rtype: InlineKeyboardMarkup
		"""
		markup = InlineKeyboardMarkup()
		buttons = []

		for i_month, month in self.__months.items():
			if i_month < self.min_date.month and self.min_date.year == year:
				button = InlineKeyboardButton(text=" ", callback_data=f"wrong_date:{year} {i_month}")

			else:
				button = InlineKeyboardButton(text=month, callback_data=f"__month:{year} {i_month}")

			buttons.append(button)

			if len(buttons) == 3:
				markup.add(*buttons)
				buttons = []

		prev_button_sym, prev_button_data = self.__last_year(year=year)
		next_button_sym, next_button_data = self.__next_year(year=year)

		prev_button = InlineKeyboardButton(text=prev_button_sym, callback_data=prev_button_data)
		middle_button = InlineKeyboardButton(text=year, callback_data=f'__years:{self.min_date.year}')
		next_button = InlineKeyboardButton(text=next_button_sym, callback_data=next_button_data)

		markup.add(prev_button, middle_button, next_button)

		return markup

	def years(self, year: int) -> InlineKeyboardMarkup:
		"""
		Функция, которая создаёт клавиатуру со списком годов.
		:param year: год.
		:type year: int
		:return: клавиатура со списком годов.
		:rtype: InlineKeyboardMarkup
		"""
		markup = InlineKeyboardMarkup()

		years = []

		for year_ in range(year, self.max_date.year + 1):
			button = InlineKeyboardButton(text=year_, callback_data=f"__months:{year_}")
			years.append(button)

			if len(years) == 2:
				markup.add(*years)
				years = []

		if years:
			markup.add(*years)

		return markup

	def __last_year(self, year: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить предыдущий год. Если можно, то указывает предыдущий год.
		:param year: год.
		:return: text_button, callback_data_button
		:rtype: tuple
		"""
		if self.min_date.year == year:
			return " ", f"None:{year}"

		return "<", f"__months:{year - 1}"

	def __next_year(self, year: int) -> Tuple[str, str]:
		"""
		Функция, которая проверяет можно ли отобразить следующий год. Если можно, то указывает следующий год.
		:param year: год.
		:return: text_button, callback_data_button
		:rtype: tuple
		"""
		if self.max_date.year == year:
			return " ", f"None:{year}"

		return ">", f"__months:{year + 1}"
