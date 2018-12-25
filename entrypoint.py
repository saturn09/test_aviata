import asyncio
from datetime import datetime, timedelta
from itertools import product
from dateutil.rrule import rrule, DAILY

from core.entities import Api, View
from core.creds import Route


async def main():
    api = Api()
    today = datetime.now()
    tasks = []

    route_date = product(
        [r for r in Route],
        [d for d in rrule(freq=DAILY, dtstart=today, count=31)])

    for route, date in route_date:
        task = asyncio.ensure_future(api.list_flights(route, date))
        tasks.append(task)

    flights = await asyncio.gather(*tasks)
    cheapest = [min(route_flights, key=lambda flight: flight.price).to_dict() for route_flights in flights if route_flights]

    View.to_csv(
        data=cheapest,
        path=f"flights_{today.strftime('%Y-%m-%d')}_{(today + timedelta(days=30)).strftime('%Y-%m-%d')}.csv"
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
