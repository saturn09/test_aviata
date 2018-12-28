import asyncio
from datetime import datetime
from itertools import product
from dateutil.rrule import rrule, DAILY

from core.entities import Api, View
from core.creds import Route

REQUEST_PER_SEC = 65


async def main():
    api = Api()
    tasks = []

    route_date = list(product(
        [r for r in Route],
        [d for d in rrule(freq=DAILY, dtstart=datetime.now(), count=31)]))

    flights = []

    while route_date:
        """
        Отправка запросов частями, потому что сервер возвращает статусы 500 и 502 при
        большом кол-ве запросов в секунду.
        """
        for route, date in route_date[:REQUEST_PER_SEC]:
            task = asyncio.ensure_future(api.list_flights(route, date))
            tasks.append(task)

        flights.extend(await asyncio.gather(*tasks))
        del tasks[:REQUEST_PER_SEC]
        del route_date[:REQUEST_PER_SEC]

    cheapest = [min(route_flights, key=lambda flight: flight.price).to_dict()
                for route_flights in flights if route_flights]

    View.to_csv(cheapest,
                f'flights_for_30_days_from_{datetime.today().strftime("%Y-%m-%d")}')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
