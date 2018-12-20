from pprint import pprint
from datetime import datetime

import requests as r

from .creds import TOKEN, Route
from .utils import handle_response, is_ready, get_logger


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
        return [Flight.from_json(j) for j in self.api.flights_info(id_).json()['items']]


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
            f"Price - {self.price or ''}"

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
            'Price': self.price
        }


class View:
    @classmethod
    def to_csv(cls, data: dict):
        pass


if __name__ == '__main__':
    api = Api()
    c = Client(api)
    flights = c.list_flights(Route.ALA_CIT, datetime(2019, 1, 1))
    pprint(flights)
