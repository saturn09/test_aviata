import os

import pandas as pd


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
        df = pd.DataFrame(sorted(data, key=lambda x: x['Departure Time']))
        _, ext = os.path.splitext(path)
        if not ext:
            path += '.csv'

        path = os.path.join(parent_dir or cls.cache, path)
        df.to_csv(path, sep=';', encoding='utf-8')
