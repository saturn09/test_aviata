import asyncio
import logging

from .entities import AsyncResponse

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(filename=name + '.log')
    fh.setLevel(logging.ERROR)
    frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(msg)s')
    sh.setFormatter(frmt)
    fh.setFormatter(frmt)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


def handle_response(req):
    """
    Переотправляет запросы при ошибках или неожиданных кодах статуса

    :param req: request function
    :return: response
    """
    async def handled(self, method, url, _json=None):
        timeout = 5
        while True:
            try:
                response = await req(self, method, url, _json)
                if response.status not in [200, 201]:
                    raise ConnectionError(
                        f'API returned response with {response.status} status code')
            except Exception as e:  # Отлавливать все исключения плохо, но стоит обезопаситься от нежданных ошибок
                self.logger.exception(e)
            else:
                return AsyncResponse(
                    text=await response.text(),
                    json=await response.json(),
                    status_code=response.status
                )
            finally:
                await asyncio.sleep(timeout)
    return handled


def is_ready(func):
    """
    Проверяет если статус ответа по информации о рейсе имеет значение "done"

    :param func: функция получения информации о рейсе
    :return: полезная нагрузка [price, date, dep, arr, flight, etc.]
    """
    async def asserted(self, id_):
        timeout = 5
        while True:
            response = await func(self, id_)
            if response.json['status'] == 'done':
                return response
            else:
                await asyncio.sleep(timeout)
    return asserted
