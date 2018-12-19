import time


def handle_response(req):
    """
    Re-sends requests on exceptions or inappropriate status codes

    :param req: request function
    :return: response
    """
    def handled(self, method, url, _json):
        attempts = 3
        timeout = 10
        while attempts:
            try:
                response = req(self, method, url, _json)
                if response.status_code not in [200, 201]:
                    raise ConnectionError(
                        f'API returned response with {response.status_code} status code')
            except Exception as e:  # Отлавливать все исключения плохо, но стоит обезопаситься от нежданных ошибок
                self.logger.exception(e)
            else:
                return response
            finally:
                attempts -= 1
                time.sleep(timeout)
    return handled


def is_ready(func):
    """
    Checks if status of response is "done"

    :param func: route info fetcher
    :return: route payload [price, date, dep, arr, flight, etc.]
    """
    def asserted(self, id_):
        attempts = 3
        timeout = 5
        while attempts:
            response = func(id_)
            if response.json()['status'] == 'done':
                return response
            else:
                time.sleep(timeout)
    return asserted
