from config_data.config import RAPID_API_KEY
from typing import Dict, Any, Optional
from typing import Iterable
from utils.request_to_api import request_to_api
from datetime import date
from requests.exceptions import Timeout, RequestException, ConnectionError

def get_city_id(city: str) -> Optional[Dict[str, str]]:
	"""
	Функция, которая возвращает название и ID города.
	:param city: название города, ID которого нужно найти.
	:type city: str
	:return: Словарь, где ключ - это найденный(е) город(а), а значение - ID этого(их) города(ов).
	:rtype: dict
	"""
	result = {}

	url = "https://hotels4.p.rapidapi.com/locations/v3/search"

	querystring = {"q": city, "locale": "ru_RU"}

	headers = {
		"X-RapidAPI-Key": RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	try:
		data = request_to_api(method="GET", url=url, headers=headers, params=querystring)

		if data:
			for i_dict in data["sr"]:
				if i_dict["type"] in ("CITY", "NEIGHBORHOOD"):
					result[i_dict["gaiaId"]] = i_dict["regionNames"]["fullName"]

			return result
		return None

	except (KeyError, Timeout, RequestException, ConnectionError):
		return None

def get_hotels(command: str,
			   region_Id: str,
			   check_In_Date: date,
			   check_Out_Date: date,
			   count_hotels: int,
			   sort: str,
			   count_photos: int = 0,
			   params: Optional[dict] = None) -> Iterable[Dict[str, Any]]:
	"""
	Функция генератор, которая возвращает словарь с полными данными об отеле в выбранном городе.
	:param command: введённая команда.
	:param region_Id: id города.
	:param check_In_Date: дата заезда.
	:param check_Out_Date: дата выезда.
	:param count_hotels: количество отелей.
	:param sort: тип сортировки
	:param count_photos: количество фотографий отеля
	:param params: словарь с максимальной и минимальной ценой для команды 'bestdeal'
	"""
	url = "https://hotels4.p.rapidapi.com/properties/v2/list"

	payload = {
		"currency": "USD",
		"locale": "ru_RU",
		"destination": {"regionId": region_Id},
		"checkInDate": {
			"day": check_In_Date.day,
			"month": check_In_Date.month,
			"year": check_In_Date.year
		},
		"checkOutDate": {
			"day": check_Out_Date.day,
			"month": check_Out_Date.month,
			"year": check_Out_Date.year
		},
		"rooms": [{"adults": 1}],
		"resultsStartingIndex": 0,
		"resultsSize": count_hotels,
		"sort": sort,
		"filters": {"price": {
			"max": 0,
			"min": 0
		}}
	}

	if command == "bestdeal":
		payload["filters"]["price"]["max"] = params["max_price"]
		payload["filters"]["price"]["min"] = params["min_price"]
		payload["resultsSize"] += 7

	else:
		payload.pop("filters")

	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	try:
		data = request_to_api(method="POST", url=url, json=payload, headers=headers)

		if data:
			if data["data"] is not None:
				hotels = data["data"]["propertySearch"]["properties"]

				if command == "highprice":
					hotels = sorted(hotels, key=lambda hotel: hotel["price"]["lead"]["amount"], reverse=True)

				for property in hotels:
					result = get_hotel_info(property_Id=property["id"], count_photos=count_photos)

					result["name"] = property["name"]

					date_in = check_In_Date.strftime("%Y-%m-%d")
					date_out = check_Out_Date.strftime("%Y-%m-%d")

					result["link"] = f'https://www.hotels.com/h{property["id"]}.Hotel-Information' \
									 f'/?chkin={date_in}&chkout={date_out}&x_pwa=1&rm1=a1'

					distance = property["destinationInfo"]["distanceFromDestination"]["value"]
					result["distance"] = f"{distance} км"
					price = property["price"]["lead"]["formatted"]
					result["price_str"] = get_price_str(line=price)
					result["price"] = property["price"]["lead"]["amount"]
					total_price = property["price"]["displayMessages"][1]["lineItems"][0]["value"]
					result["total_price"] = get_price_str(line=total_price)

					yield result
			else:
				yield None
		else:
			yield None

	except (KeyError, Timeout, RequestException, ConnectionError):
		yield None

def get_hotel_info(property_Id: str,
				   count_photos: int = 0) -> Optional[Dict[str, Any]]:
	"""
	Функция, которая собирает информацию об отеле, а именно:
	- адрес отеля,
	- координаты отеля (долгота и широта),
	- рейтинг отеля,
	- изображения отеля (если в функцию передали аргумент count_pictures)

	:param property_Id: передаётся Id отеля
	:type property_Id: str
	:param count_photos: передаётся количество изображений
	:type count_photos: int
	:return: словарь с краткой информацией об отеле
	:rtype: dict
	"""
	url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

	payload = {
		"locale": "ru_RU",
		"propertyId": property_Id
	}

	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": RAPID_API_KEY,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	try:
		data = request_to_api(method="POST", url=url, json=payload, headers=headers)

		if data:
			if data["data"]["propertyInfo"]["summary"]["overview"]["propertyRating"] is not None:
				rating = int(data["data"]["propertyInfo"]["summary"]["overview"]["propertyRating"]["rating"])
				rating = rating * "⭐"

			else:
				rating = ''

			result = {
				"address": data["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"],
				"latitude": data["data"]["propertyInfo"]["summary"]["location"]["coordinates"]["latitude"],
				"longitude": data["data"]["propertyInfo"]["summary"]["location"]["coordinates"]["longitude"],
				"rating": rating,
				"photos": []
			}

			if count_photos > 0:
				for image in data["data"]["propertyInfo"]["propertyGallery"]["images"]:
					result["photos"].append(image["image"]["url"])

					if len(result["photos"]) == count_photos:
						break

			return result

	except (KeyError, Timeout, RequestException, ConnectionError):
		return None

def get_price_str(line: str) -> str:
	"""
	Функция, которая возвращает стоимость отеля.
	:param line: строка.
	:type line: str
	:return: result
	:rtype: str
	"""
	result = ''

	for sym in line:
		if sym.isdigit():
			result += sym

		elif sym == ',':
			result += ' '

	result += " $"

	return result

def get_hotel_info_str(data: dict, count_nights: int) -> str:
	"""
	Функция, которая собирает всю информацию об отеле в одно сообщение.
	:param count_nights: количество ночей
	:type count_nights: int
	:param data: словарь с данными об отеле.
	:type data: dict
	:return: text
	:rtype: str
	"""
	text = f"🏠 <b>{data['name']}</b> {data['rating']}\n" \
		   f"📍 <b>Адрес:</b> {data['address']}\n" \
		   f"🚕 <b>Расстояние до центра города:</b> {data['distance']}\n" \
		   f"💵 <b>Цена за 1 ночь:</b> от {data['price_str']}\n" \
		   f"💰 <b>Примерная стоимость за {count_nights} ноч:</b> {data['total_price']} (проживание + налог)\n" \
		   f'🛎️ <a href = "{data["link"]}">Ссылка на страницу с отелем</a>'

	return text
