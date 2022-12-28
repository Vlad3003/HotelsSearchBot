import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
	exit('Переменные окружения не загружены т.к отсутствует файл .env')

else:
	load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
	('start', "Перезапустить бота"),
	('help', "Помощь"),
	('lowprice', 'Топ самых дешёвых отелей в городе'),
	('highprice', 'Топ самых дорогих отелей в городе'),
	('bestdeal', 'Топ отелей, наиболее подходящих по цене и расположению от центра'),
	('history', 'История поиска отелей'),
	('delete_history', 'Очистить историю поиска')
)
LOG_PATH = os.path.abspath(os.path.join("logs", "debug.log"))
