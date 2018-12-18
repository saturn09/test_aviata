import logging
import time
from enum import Enum
from datetime import datetime
from pprint import pprint

import requests as r


class Route(Enum):
    ALA_TSE = 'ALA-TSE'
    TSE_ALA = 'TSE-ALA'
    ALA_MOW = 'ALA-MOW'
    MOW_ALA = 'MOW-ALA'
    ALA_CIT = 'ALA-CIT'
    CIT_ALA = 'CIT-ALA'
    TSE_MOW = 'TSE-MOW'
    MOW_TSE = 'MOW-TSE'
    TSE_LED = 'TSE-LED'
    LED_TSE = 'LED-TSE'


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(filename=name + '.log')
    fh.setLevel(logging.DEBUG)
    frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(msg)s')
    sh.setFormatter(frmt)
    fh.setFormatter(frmt)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


class AviataApi:
    def __init__(self):
        self.base_url = 'https://api.platform.​staging.aviata.team​/airflow/'
        self.token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzMWM1ZDZmNy03NGJh" \
                     "LTRmZGUtOGYyMS1kN2JhNDE4YTI3MWMiLCJpc3MiOiJ2RjJmMUNtSHlzYmRGdmJkR" \
                     "1ZVdE5BNkd3WGplOWhKeiIsImlhdCI6MTU0Mjg4MzA0NSwiZXhwIjoyODY3Mzk1MD" \
                     "Q1LCJjb25zdW1lciI6eyJpZCI6ImQ5YjNlNzlmLTQ4YTYtNDM3ZC05MDViLTk3NzQ" \
                     "4ZWVmMDVlZCIsIm5hbWUiOiJjaG9jby1rei5ob3N0In19.oAcPmer0vsnSZeKUmMv" \
                     "Pj0emnQopIQKWcaPg7-_cQgA"
        self._sesh = r.Session()
        self._sesh.headers.update({'Authorization': f'Bearer {self.token}'})
        self.logger = get_logger('main')

    def _request(self, method: str, url: str, _json):
        if method == 'GET':
            resp = self._sesh.get(url)
        else:
            resp = self._sesh.post(url, json=_json)
        return resp

    def _handle_response(self, method, url, _json):
            attempts = 3
            timeout = 10
            while attempts:
                try:
                    response = self._request(method, url, _json)
                    if response.status_code not in [200, 201]:
                        raise r.RequestException(f'API returned response with {response.status_code} status code')
                except Exception as e:  # Отлавливать все исключения плохо, но стоит обезопаситься от нежданных ошибок
                    self.logger.exception(e)
                else:
                    return response
                finally:
                    attempts -= 1
                    time.sleep(timeout)

    def request(self, method, url, _json=None):
        return self._handle_response(method, url, _json)

    def search(self, route: Route, date: datetime):
        self.logger.info(f'Search flight with {route.value} route at {date}')
        url = self.base_url + 'search'
        payload = {'query': f'{route.value}{date.strftime("%Y%m%d")}1000E'}
        return self.request('POST', url, _json=payload)

    def search_multiple(self, routes: list or tuple, date: datetime):
        flights = {date.strftime('%Y-%m-%d'): {}}
        for route in routes:
            id_ = self.search(route, date).json()['id']
            flights[date.strftime('%Y-%m-%d')][route] = self.get_flights(id_)
        return flights

    def get_flights(self, _id):
        self.logger.info(f'Check if {_id} result is ready')
        url = self.base_url + f'search/results/{_id}'
        resp = None
        while resp and resp.json()['status'] != 'done':
            resp = self.request(method='GET', url=url)
        else:
            return resp



if __name__ == '__main__':
    api = AviataApi()
    res = api.search(Route.ALA_CIT, datetime(2019, 1, 1))
    _id = res.json()['id']
    res = api.get_flights(_id)
    pprint(res.json()['items'])


