import requests
from typing import Optional

def request_to_api(**kwargs) -> Optional[dict]:
	"""
	Функция, которая совершает запрос к API. Если статус 200, то возвращает словарь с полученными данными,
	иначе None
	:return: словарь с данными
	"""
	response = requests.request(**kwargs, timeout=20)

	if response.status_code == requests.codes.ok:
		return response.json()
	return None
