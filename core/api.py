from datetime import datetime

import aiohttp

from .creds import TOKEN, Route
from .entities import Flight
from .utils import handle_response, is_ready, get_logger


class Api:
    def __init__(self):
        self.base_url = 'https://api.platform.​staging.aviata.team​/airflow/'
        self.token = TOKEN
        self._headers = {'Authorization': f'Bearer {self.token}'}
        self.logger = get_logger('main')

    @handle_response
    async def async_request(self, method, url, _json=None):
        async with aiohttp.ClientSession(headers=self._headers) as session:
            return await session.request(method, url, json=_json)

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


