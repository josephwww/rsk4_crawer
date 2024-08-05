import asyncio

from const import *
from craw_utils import Rsk4CrawUtils


class Rsk4CrawFactory(Rsk4CrawUtils):
    """
    check_form_list是由字典组成的列表，字典结构为：
    {
        "ENTRY_ID": 查验单对应报关单id,
        "CHECK_FORM_ID": 查验单id,
        "CREATE_TIME": 查验单创建时间，即中控时间
        "G_NOS": 商品项编号列表,
        "FILES": 危化品单证文件列表: dict: {'g_no': 商品编码, 'code': 文件编号, 'filename': 文件名}
    }
    """
    def __init__(self):
        super().__init__()
        self.check_form_list = []

    def craw_pending_order(self):
        """
        查询未接单，收集查验资质为危包查验资质的查验单
        危包查验资质的查验单: CHECK_CERTS 包含 'SJ1' 的查验单
        :return: list: {"ENTRY_ID": <报关单号>, "CHECK_FORM_ID": <查验单uuid>}
        """
        response_data = self.post_form_data(ORDER_LIST_URL, ORDER_LIST_PARAMS).json()
        # 访问data列表
        data_list = response_data.get('data', [])

        if data_list:
            for item in data_list:
                if item['ENTRY_ID'] and item['CHECK_FORM_ID'] and item['CHECK_CERTS'] \
                        and HARZ_CERT in item['CHECK_CERTS']:
                    check_form = {
                        "ENTRY_ID": item['ENTRY_ID'],
                        "CHECK_FORM_ID": item['CHECK_FORM_ID'],
                        "CREATE_TIME": item['CREATE_TIME'],  # 查验单创建时间，即中控时间
                        "G_NOS": [],
                        "FILES": []
                    }
                    self.check_form_list.append(check_form)

    def craw_inspection_order(self):
        """
        查询人工查验单，筛选查验场地为‘皇岗进口危化’的查验单
        :return:
        """
        response_data = self.post_form_data(CHECK_LIST_URL, CHECK_LIST_PARAMS).json()
        # 访问data列表
        data_list = response_data.get('data', [])

        if data_list:
            for item in data_list:
                if item['ENTRY_ID'] and item['CHECK_FORM_ID'] and item['CHECK_CERTS']:
                    check_form = {
                        "ENTRY_ID": item['ENTRY_ID'],
                        "CHECK_FORM_ID": item['CHECK_FORM_ID'],
                        "CREATE_TIME": item['CREATE_TIME'],  # 查验单创建时间，即中控时间
                        "G_NOS": [],
                        "FILES": []
                    }
                    self.check_form_list.append(check_form)

    def get_entry_info(self):
        """
        获取报关所有商品项列表
        :param check_form_list:
        :return:
        """
        for check_form in self.check_form_list:
            check_form_id = check_form['CHECK_FORM_ID']
            entry_id = check_form['ENTRY_ID']

            ENTRY_LIST_PARAMS['checkFormId'] = check_form_id
            response = self.post_form_data(ENTRY_LIST_URL, ENTRY_LIST_PARAMS).json()
            entry_list = response.get('data')
            for entry_g_no in entry_list:
                if not self.judge_is_exist(entry_id, entry_g_no['G_NO']):
                    check_form['G_NOS'].append(entry_g_no['G_NO'])

    def get_entry_ddate(self):
        """
        将有效的报关单查询申报时间，注入D_DATE
        :param check_form_list:
        :return:
        """
        for check_form in self.check_form_list:
            if check_form['G_NOS']:
                check_form_id = check_form['CHECK_FORM_ID']
                entry_id = check_form['ENTRY_ID']
                DDATE_PARAMS['entryId'] = entry_id
                DDATE_PARAMS['checkFormId'] = check_form_id
                response = self.post_form_data(DDATE_URL, DDATE_PARAMS).json()
                entry_info = response.get('data')
                check_form['D_DATE'] = entry_info.get('D_DATE')

    def get_data_document_info(self):
        """
        获取所有文件信息
        :param check_form_list:
        :return:
        """
        for check_form in self.check_form_list:
            if check_form['G_NOS']:
                chk_form_id = check_form['CHECK_FORM_ID']
                entry_id = check_form['ENTRY_ID']
                g_nos = check_form['G_NOS']
                print(f'CHECK_FORM_ID: {chk_form_id}; ENTRY_ID: {entry_id}; G_NOS: {g_nos}')
                for g_no in g_nos:
                    DOCUMENT_LIST_PARAMS['checkFormId'] = chk_form_id
                    DOCUMENT_LIST_PARAMS['gNo'] = g_no
                    response = self.post_form_data(DOCUMENT_LIST_URL, DOCUMENT_LIST_PARAMS).json()
                    doc_list = response.get('data')
                    for doc in doc_list:
                        doc_type = doc.get('DOCU_TYPE')
                        doc_filename = DOC_TYPE_DICT.get(doc_type)
                        doc_code = doc.get('DOCU_CODE')
                        check_form['FILES'].append({'g_no': g_no, 'code': doc_code, 'filename': doc_filename})

    async def get_document_pdf(self):
        """
        下载所有pdf并上传minio
        :param check_form_list:
        :return:
        """
        async_tasks = []
        for check_form in self.check_form_list:
            for check_form_file in check_form['FILES']:
                entry_id = check_form['ENTRY_ID']
                g_no = check_form_file['g_no']
                filename = check_form_file['filename']
                doc_code = check_form_file['code']
                response = self.post_data_file(url=GET_PDF_URL.format(get_pdf_base_url=GET_PDF_BASE_URL, doc_code=doc_code))
                file_path = MINIO_PDF_FILE_PATH.format(entry_id=entry_id, g_no=g_no, filename=filename)

                task = asyncio.create_task(self.upload_pdf_to_minio("sjdt-ocr", file_path, response.content))
                async_tasks.append(task)
                self.save_mysql(entry_id=entry_id, g_no=g_no, flag='PENDING', file_name=filename,
                                ddate=check_form['D_DATE'], create_time=check_form['CREATE_TIME'])

        # 等待所有上传minio结束
        await asyncio.gather(*async_tasks)
