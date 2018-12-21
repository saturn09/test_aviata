from datetime import datetime
from itertools import product
from dateutil.rrule import rrule, DAILY
from pprint import pprint

from core.main import Api
from core.creds import Route

if __name__ == '__main__':
    api = Api()
    for route, date in product(
            [r for r in Route],
            [d for d in rrule(freq=DAILY, dtstart=datetime.now(), count=30)]
    ):
        flights = api.list_flights(route, date)
        pprint(flights)
