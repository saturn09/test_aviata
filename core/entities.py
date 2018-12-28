import os
from datetime import datetime

import pandas as pd
import aiohttp

from .utils import handle_response, is_ready, get_logger
from .creds import TOKEN, Route


class Api:
    def __init__(self):
        self.base_url = 'https://api.platform.​staging.aviata.team​/airflow/'
        self.token = TOKEN
        self._headers = {'Authorization': f'Bearer {self.token}'}
        self.logger = get_logger('main')

    @handle_response
    async def async_request(self, method, url, _json=None):
        async with aiohttp.ClientSession(headers=self._headers) as session:
            resp = await session.request(method, url, json=_json)
            a_resp = AsyncResponse(
                text=await resp.text(),
                json=await resp.json(),
                status_code=resp.status
            )
            return a_resp

    async def route_id(self, route: Route, date: datetime):
        self.logger.info(f'Get ID for {route.value} route at {date}')
        url = self.base_url + 'search'
        payload = {'query': f'{route.value}{date.strftime("%Y%m%d")}1000E'}
        return await self.async_request(method='POST', url=url, _json=payload)

    @is_ready
    async def flights_info(self, id_):
        self.logger.info(f'Get flights by {id_} ID')
        url = self.base_url + f'search/results/{id_}'
        return await self.async_request(method='GET', url=url)

    async def list_flights(self, route: Route, date: datetime):
        route_id = await self.route_id(route, date)
        id_ = route_id.json['id']
        flights = await self.flights_info(id_)
        return [Flight.from_json(j) for j in flights.json['items']]


class AsyncResponse:
    def __init__(self, text, json, status_code):
        """
        Принимает данные из асинхронного запроса в api
        и формирует Пользовательский Ответ.
        Используется по причине возвращения
        функцией-запросом - корутины, вместо объекта Ответ

        :param text:
        :param json:
        :param status_code:
        """
        self.text = text
        self.json = json
        self.status_code = status_code


class Flight:
    def __init__(self, route, dep, arr, dep_at,
                 arr_at, airline, price=None):
        self.route = route
        self.dep = dep
        self.arr = arr
        self.dep_at = dep_at
        self.arr_at = arr_at
        self.price = price
        self.airline = airline
        self.transit_flights = []

    def __repr__(self):
        return f"Flight: Route - {self.route}\n" \
            f"Departure - {self.dep}\n" \
            f"Arrival - {self.arr}\n" \
            f"Departure Time - {self.dep_at}\n" \
            f"Arrival Time - {self.arr_at}\n" \
            f"Airline - {self.airline}\n" \
            f"Price - {self.price or ''}\n" \
            f"Transits - {self.transit_flights}"

    @classmethod
    def from_json(cls, json_: dict):
        route = json_['$meta']['search_query'][:7]
        f = cls(
            route=route,
            dep=json_['flights'][0]['segments'][0]['dep']['airport'],
            arr=json_['flights'][0]['segments'][0]['arr']['airport'],
            dep_at=json_['flights'][0]['segments'][0]['dep']['at'],
            arr_at=json_['flights'][0]['segments'][0]['arr']['at'],
            price=json_['price']['amount'],
            airline=json_['flights'][0]['segments'][0]['airline'],
        )
        if len(json_['flights'][0]['segments']) > 1:
            for flight in json_['flights'][0]['segments'][1:]:
                f.transit_flights.append(
                    cls(
                        route=route,
                        dep=flight['dep']['airport'],
                        arr=flight['arr']['airport'],
                        dep_at=flight['dep']['at'],
                        arr_at=flight['arr']['at'],
                        airline=flight['airline']
                    )
                )
        return f

    def to_dict(self):
        return {
            'Route': self.route,
            'Departure': self.dep,
            'Arrival': self.arr,
            'Departure Time': self.dep_at,
            'Arrival Time': self.arr_at,
            'Airline': self.airline,
            'Price': self.price,
            'Transits': self.transit_flights
        }


class View:
    cache = 'cache'

    if not os.path.exists(cache):
        os.mkdir(cache)

    @classmethod
    def to_csv(cls, data: list, path: str, parent_dir: str = None):
        """
        Записывает данные в табличном представлении .csv

        :param data: данные для записи
        :param path: путь к конечному файлу
        :param parent_dir: директория в которую будет записан файл
        :return: None
        """
        flights_df = pd.DataFrame(data)
        flights_df = flights_df.sort_values(by=['Departure Time', 'Route'])
        _, ext = os.path.splitext(path)
        if not ext:
            path += '.csv'
        path = os.path.join(parent_dir or cls.cache, path)
        flights_df.to_csv(path, sep=';', encoding='utf-8')
