from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def yes_or_no_keyboard() -> InlineKeyboardMarkup:
	"""
	Функция, которая создаёт клавиатуру с кнопками Да и Нет.
	:return: None
	"""
	markup = InlineKeyboardMarkup()

	button_yes = InlineKeyboardButton(text="Да", callback_data="yes")
	button_no = InlineKeyboardButton(text="Нет", callback_data="no")

	markup.add(button_yes, button_no)

	return markup
