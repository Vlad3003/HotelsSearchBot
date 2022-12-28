import peewee
from loader import db

class BaseModel(peewee.Model):
	"""Базовый класс для создания таблиц в БД."""
	class Meta:
		database = db

class User(BaseModel):
	"""
	Класс для создания таблицы 'users' в БД.

	Attributes:
		name (str): имя
		username (str): имя пользователя
		telegram_id (int): Телеграм id пользователя
		chat_id (int): чат id
		date (str): дата ввода команды
		command (str): название команды
		request_parameters (str): параметры запроса
		result (str): найденные отели
	"""
	name = peewee.TextField(column_name="name")
	username = peewee.TextField(column_name="username")
	telegram_id = peewee.IntegerField(column_name="telegram_id")
	chat_id = peewee.IntegerField(column_name="chat_id")
	date = peewee.TextField(column_name="date")
	command = peewee.TextField(column_name="command")
	request_parameters = peewee.TextField(column_name="request_parameters")
	result = peewee.TextField(column_name="result")

	class Meta:
		db_table = "users"
		order_by = "rowid"
