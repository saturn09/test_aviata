from pprint import pprint

from core.main import Api, Client
from core.creds import Route

if __name__ == '__main__':
    api = Api()
    c = Client(api)
    flights = c.list_flights(Route.ALA_CIT, datetime(2019, 1, 1))
    pprint(flights)
