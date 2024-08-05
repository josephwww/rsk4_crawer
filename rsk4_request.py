import requests
import time
from functools import wraps

from const import TICKET_REFRESH_URL, TICKET_URL, MAX_RETRIES, DELAY
from login_script import get_rsk4_cookie


cookies = get_rsk4_cookie()


def get_ticket_code_whp():
    # 获取最新ticket，防止请求失败
    response = requests.get(TICKET_REFRESH_URL, cookies=cookies)
    ticket_data = response.json()
    # 访问data列表
    ticket_code_data = ticket_data['data']
    return ticket_code_data


ticket_code = get_ticket_code_whp()


def rsk4_requests_handler(use_ticket=False):
    def decorator(func):
        @wraps(func)
        def wrapper(url, *params):
            global ticket_code
            if use_ticket:
                url = TICKET_URL.format(base_url=url, ticket_code=ticket_code)
            retries = 0
            while retries < MAX_RETRIES:
                response = func(url, *params)
                if response.status_code == 200:
                    return response
                else:
                    retries += 1
                    ticket_code = get_ticket_code_whp()
                    time.sleep(DELAY)
            raise Exception(f"Failed to get a successful response after {MAX_RETRIES} retries")
        return wrapper
    return decorator


@rsk4_requests_handler(use_ticket=True)
def post_form_data(url, data):
    return requests.post(url, data=data)


@rsk4_requests_handler(use_ticket=True)
def post_data_file(url):
    return requests.get(url, stream=True)
