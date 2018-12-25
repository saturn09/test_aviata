import asyncio
from datetime import datetime
from itertools import product
from dateutil.rrule import rrule, DAILY
from pprint import pprint

from core.main import Api
from core.creds import Route

import pandas as pd


async def main():
    api = Api()
    tasks = []

    route_date = product(
        [r for r in Route],
        [d for d in rrule(freq=DAILY, dtstart=datetime.now(), count=30)])

    for route, date in route_date:
        task = asyncio.ensure_future(api.list_flights(route, date))
        tasks.append(task)

    flights = await asyncio.gather(*tasks)
    cheapest = [min(f, key=lambda x: x.price) for f in flights if f]
    cheapest_as_dict = [c.to_dict() for c in cheapest]

    table = pd.DataFrame(cheapest_as_dict)
    pprint(table)
    table.to_csv('test.csv', sep=',', encoding='utf-8')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
