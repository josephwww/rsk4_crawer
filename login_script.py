import os
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_rsk4_cookie():
    # 配置Chrome选项
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 启动Chrome浏览器
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)

    try:
        # 打开登录页面
        driver.get('http://10.226.8.11/CustomsInspectionWeb')

    # 等待重定向并获取元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'signInName'))
        )

        # 输入用户名和密码
        username = driver.find_element(By.ID, 'signInName')
        password = driver.find_element(By.ID, 'password')
        username.send_keys(os.getenv('H4A_USERNAME'))
        password.send_keys(os.getenv('H4A_PASSWORD'))

        # 提交表单
        login_button = driver.find_element(By.ID, 'ctl02_SignInButton')
        login_button.click()

        # 等待页面加载并获取重定向后的cookie
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'LAY_app_body'))
        )

        cookies = driver.get_cookies()

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
    return {cookie['name']: cookie['value'] for cookie in cookies}


def get_ticket_code_whp():
    # 获取最新ticket，防止请求失败
    url = 'http://10.226.8.11/CustomsInspectionWeb/Ticket/Refresh'
    response = requests.get(url, cookies=get_rsk4_cookie())

    # 解析为python字典
    ticket_data = response.json()
    # 访问data列表
    ticket_code_data = ticket_data['data']

    return ticket_code_data


if __name__ == '__main__':
    get_rsk4_cookie()
