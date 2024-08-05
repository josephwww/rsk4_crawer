import io
import uuid
import os
import requests
import time
from functools import wraps

from minio import Minio
from minio.error import S3Error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from const import *
from models import HazardousPdfTask


class Rsk4CrawUtils:
    def __init__(self):
        self.ticket = self.get_ticket_code_whp()
        self.session = self.get_mysql_session()
        self.minio_client = self.get_minio_client()

    # 入库
    def save_mysql(self, entry_id, g_no, flag=None, file_name=None, ddate=None, create_time=None) -> HazardousPdfTask:
        task = self.session.query(HazardousPdfTask).filter(HazardousPdfTask.entry_id == entry_id) \
            .filter(HazardousPdfTask.g_no == g_no).first()

        if not task:
            task = HazardousPdfTask(
                id=str(uuid.uuid4()),
                entry_id=entry_id,
                g_no=g_no,
                ddate=ddate,
                create_time=create_time
            )
            self.session.add(task)
            self.session.commit()

        if flag:
            if file_name == HarzFileName.declaration.value:
                task.declaration_status = flag
            if file_name == HarzFileName.label.value:
                task.label_status = flag
            if file_name == HarzFileName.instruction.value:
                task.instruction_status = flag

            self.session.commit()
        return task

    @staticmethod
    def get_mysql_session():
        mysql_szdt_engine = create_engine(os.getenv("MYSQL_SZDT_URL"), echo=False, pool_pre_ping=True)
        session_mysql_szdt = sessionmaker(autocommit=False, autoflush=True, bind=mysql_szdt_engine)
        return session_mysql_szdt()

    @staticmethod
    def get_minio_client():
        minio_client = Minio(
            os.getenv("MINIO_ADDRESS"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False
        )
        return minio_client

    def judge_is_exist(self, entry_id, g_no):
        """
        判断该entry_id和g_no是否已爬取过
        :param entry_id:
        :param g_no:
        :return:
        """
        return self.session.query(HazardousPdfTask).filter(HazardousPdfTask.entry_id == entry_id) \
            .filter(HazardousPdfTask.g_no == g_no).count() > 0

    @staticmethod
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

    def get_ticket_code_whp(self):
        # 获取最新ticket，防止请求失败
        response = requests.get(TICKET_REFRESH_URL, cookies=self.get_rsk4_cookie())

        # 解析为python字典
        ticket_data = response.json()
        # 访问data列表
        ticket_code_data = ticket_data['data']

        return ticket_code_data

    async def upload_pdf_to_minio(self, bucket_name, file_path, file_data):
        file_length = len(file_data)

        # 上传文件
        try:
            self.minio_client.put_object(bucket_name, file_path, io.BytesIO(file_data), file_length)
        except S3Error as e:
            print("error: ", e)

    @staticmethod
    def rsk4_requests_handler(use_ticket=False):
        def decorator(func):
            @wraps(func)
            def wrapper(self, url, *params):
                if use_ticket:
                    url = TICKET_URL.format(base_url=url, ticket_code=self.ticket)
                retries = 0
                while retries < MAX_RETRIES:
                    response = func(self, url, *params)
                    if response.status_code == 200:
                        return response
                    else:
                        retries += 1
                        self.ticket = self.get_ticket_code_whp()
                        time.sleep(DELAY)
                raise Exception(f"Failed to get a successful response after {MAX_RETRIES} retries")
            return wrapper
        return decorator

    @rsk4_requests_handler(use_ticket=True)
    def post_form_data(self, url, data):
        return requests.post(url, data=data)

    @rsk4_requests_handler(use_ticket=True)
    def post_data_file(self, url):
        return requests.get(url, stream=True)
