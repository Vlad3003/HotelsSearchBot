from database.models import db, User
from typing import List
from loguru import logger

@logger.catch
def create_db() -> None:
	"""
	Функция, которая создаёт базу данных со следующей структурой:
	- name (str): имя
	- username (str): имя пользователя
	- telegram_id (int): Телеграм id пользователя
	- chat_id (int): чат id
	- date (str): дата ввода команды
	- command (str): название команды
	- request_parameters (str): параметры запроса
	- result (str): найденные отели
	:return: None
	"""
	with db:
		db.create_tables([User])

@logger.catch
def save_information(data: dict) -> None:
	"""
	Функция, которая сохраняет информацию в базу данных.
	:param data: словарь с данными.
	:return: None
	"""
	with db:
		name = data["name"]
		username = data["username"]
		telegram_id = data["telegram_id"]
		chat_id = data["chat_id"]
		date = data["date"]
		command = data["command"]
		request_parameters = data["request_parameters"]
		result = data["result"]

		User(name=name, username=username, telegram_id=telegram_id,
			 chat_id=chat_id, date=date, command=command,
			 request_parameters=request_parameters, result=result).save()

@logger.catch
def get_information(conditions: list) -> List[User]:
	"""
	Функция, которая возвращает информацию из базы данных.
	:param conditions: условие, при котором нужно получить информацию.
	:return: list
	"""
	with db:
		histories = [history for history in User.select().where(*conditions)]

	return histories

@logger.catch
def delete_information(telegram_id: int, chat_id: int) -> None:
	"""
	Функция, которая удаляет информацию из базы данных.
	:param telegram_id: Телеграм id.
	:type telegram_id: int
	:param chat_id: чат id
	:type chat_id: int
	:return: None
	"""
	with db:
		for history in User.select().where(User.telegram_id == telegram_id,
										   User.chat_id == chat_id):
			User.delete_instance(history)
