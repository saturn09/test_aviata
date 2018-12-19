from datetime import datetime
from pprint import pprint

import requests as r

from app.utils import handle_response, is_ready, get_logger
from creds import TOKEN, Route


class Api:
    def __init__(self):
        self.base_url = 'https://api.platform.​staging.aviata.team​/airflow/'
        self.token = TOKEN
        self._sesh = r.Session()
        self._sesh.headers.update({'Authorization': f'Bearer {self.token}'})
        self.logger = get_logger('main')

    @handle_response
    def _request(self, method: str, url: str, _json):
        return self._sesh.request(method, url, json=_json)

    def route_id(self, route: Route, date: datetime):
        self.logger.info(f'Get ID for {route.value} route at {date}')
        url = self.base_url + 'search'
        payload = {'query': f'{route.value}{date.strftime("%Y%m%d")}1000E'}
        return self._request('POST', url, _json=payload).json().get('id')

    @is_ready
    def flights_info(self, id_):
        self.logger.info(f'Get flights by {id_} ID')
        url = self.base_url + f'search/results/{id_}'
        return self._request(method='GET', url=url)


class Client:
    def __init__(self, api: Api):
        """
        Использует api для получения информации о рейсах

        :param api: источник данных о рейсах
        """
        self.api = api

    def list_flights(self, route: Route, date: datetime):
        id_ = self.api.route_id(route, date)
        return self.api.flights_info(id_).json()['items']


class View:
    @classmethod
    def to_csv(self, data: dict):
        pass


class Flight:
    def __init__(self, dep, arr, dep_at, arr_at):
        pass


if __name__ == '__main__':
    api = Api()
    c = Client(api)
    flights = c.list_flights(Route.ALA_CIT, datetime(2019, 1, 1))
    pprint(flights)
