import logging
from enum import Enum
from datetime import datetime
from pprint import pprint

import requests as r

from utils import handle_response, is_ready


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


class Api:
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

    @handle_response
    def _request(self, method: str, url: str, _json):
        return self._sesh.request(method, url, json=_json)

    def route_id(self, route: Route, date: datetime):
        self.logger.info(f'Search flight with {route.value} route at {date}')
        url = self.base_url + 'search'
        payload = {'query': f'{route.value}{date.strftime("%Y%m%d")}1000E'}
        return self._request('POST', url, _json=payload).json().get('id')

    def routes_info(self, routes: list or tuple, date: datetime):
        flights = {date.strftime('%Y-%m-%d'): {}}
        for route in routes:
            id_ = self.route_id(route, date)
            flights[date.strftime('%Y-%m-%d')][route] = self.route_info(id_)
        return flights

    @is_ready
    def route_info(self, id_):
        self.logger.info(f'Get route info by {id_} id')
        url = self.base_url + f'search/results/{id_}'
        return self._request(method='GET', url=url)


if __name__ == '__main__':
    api = Api()
    res = api.route_id(Route.ALA_CIT, datetime(2019, 1, 1))
    _id = res.json()['id']
    res = api.route_info(_id)
    pprint(res.json()['items'])
