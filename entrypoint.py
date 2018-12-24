from datetime import datetime
from itertools import product
from dateutil.rrule import rrule, DAILY
from pprint import pprint

from core.main import Api
from core.creds import Route


import asyncio


async def main(route, date):
    api = Api()

    flights = await api.list_flights(route, date)
    pprint(flights)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for route, date in product(
            [r for r in Route],
            [d for d in rrule(freq=DAILY, dtstart=datetime.now(), count=30)]
    ):
        loop.run_until_complete(main(route, date))
