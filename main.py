import asyncio

from rsk4_request import post_form_data, post_data_file
from handle import save_mysql
from handle import judge_is_exist
from const import *
from minio_utils import upload_pdf_to_minio


def craw_pending_order(check_form_list):
    """
    查询未接单，收集查验资质为危包查验资质的查验单
    危包查验资质的查验单: CHECK_CERTS 包含 'SJ1' 的查验单
    :return: list: {"ENTRY_ID": <报关单号>, "CHECK_FORM_ID": <查验单uuid>}
    """
    response_data = post_form_data(ORDER_LIST_URL, ORDER_LIST_PARAMS).json()
    # 访问data列表
    data_list = response_data.get('data', [])

    if data_list:
        for item in data_list:
            if item['ENTRY_ID'] and item['CHECK_FORM_ID'] and item['CHECK_CERTS'] and HARZ_CERT in item['CHECK_CERTS']:
                check_form = {
                    "ENTRY_ID": item['ENTRY_ID'],
                    "CHECK_FORM_ID": item['CHECK_FORM_ID'],
                    "CREATE_TIME": item['CREATE_TIME'],  # 查验单创建时间，即中控时间
                    "G_NOS": [],
                    "FILES": []
                }
                check_form_list.append(check_form)

    return check_form_list


def craw_inspection_order(check_form_list):
    """
    查询人工查验单，筛选查验场地为‘皇岗进口危化’的查验单
    :return:
    """
    response_data = post_form_data(CHECK_LIST_URL, CHECK_LIST_PARAMS).json()
    # 访问data列表
    data_list = response_data.get('data', [])

    if data_list:
        for item in data_list:
            if item['ENTRY_ID'] and item['CHECK_FORM_ID'] and item['CHECK_CERTS'] and HARZ_CERT in item['CHECK_CERTS']:
                check_form = {
                    "ENTRY_ID": item['ENTRY_ID'],
                    "CHECK_FORM_ID": item['CHECK_FORM_ID'],
                    "CREATE_TIME": item['CREATE_TIME'],  # 查验单创建时间，即中控时间
                    "G_NOS": [],
                    "FILES": []
                }
                check_form_list.append(check_form)

    return check_form_list


def get_entry_info(check_form_list):
    """
    获取报关所有商品项列表
    :param check_form_list:
    :return:
    """
    for check_form in check_form_list:
        check_form_id = check_form['CHECK_FORM_ID']
        entry_id = check_form['ENTRY_ID']

        ENTRY_LIST_PARAMS['checkFormId'] = check_form_id
        response = post_form_data(ENTRY_LIST_URL, ENTRY_LIST_PARAMS).json()
        entry_list = response.get('data')
        for entry_g_no in entry_list:
            bool_flag = judge_is_exist(entry_id, entry_g_no['G_NO'])
            if not bool_flag:
                check_form['G_NOS'].append(entry_g_no['G_NO'])


def get_entry_ddate(check_form_list):
    """
    将有效的报关单查询申报时间，注入D_DATE
    :param check_form_list:
    :return:
    """
    for check_form in check_form_list:
        if check_form['G_NOS']:
            check_form_id = check_form['CHECK_FORM_ID']
            entry_id = check_form['ENTRY_ID']
            DDATE_PARAMS['entryId'] = entry_id
            DDATE_PARAMS['checkFormId'] = check_form_id
            response = post_form_data(DDATE_URL, DDATE_PARAMS).json()
            entry_info = response.get('data')
            check_form['D_DATE'] = entry_info.get('D_DATE')


def get_data_document_info(check_form_list):
    """
    获取所有文件信息
    :param check_form_list:
    :return:
    """
    for check_form in check_form_list:
        if check_form['G_NOS']:
            chk_form_id = check_form['CHECK_FORM_ID']
            entry_id = check_form['ENTRY_ID']
            g_nos = check_form['G_NOS']
            print(f'CHECK_FORM_ID: {chk_form_id}; ENTRY_ID: {entry_id}; G_NOS: {g_nos}')
            for g_no in g_nos:
                DOCUMENT_LIST_PARAMS['checkFormId'] = chk_form_id
                DOCUMENT_LIST_PARAMS['gNo'] = g_no
                response = post_form_data(DOCUMENT_LIST_URL, DOCUMENT_LIST_PARAMS).json()
                doc_list = response.get('data')
                for doc in doc_list:
                    doc_type = doc.get('DOCU_TYPE')
                    doc_filename = DOC_TYPE_DICT.get(doc_type)
                    doc_code = doc.get('DOCU_CODE')
                    check_form['FILES'].append({'g_no': g_no, 'code': doc_code, 'filename': doc_filename})


async def get_document_pdf(check_form_list):
    """
    下载所有pdf并上传minio
    :param check_form_list: 
    :return: 
    """
    async_tasks = []
    for check_form in check_form_list:
        for check_form_file in check_form['FILES']:
            entry_id = check_form['ENTRY_ID']
            g_no = check_form_file['g_no']
            filename = check_form_file['filename']
            doc_code = check_form_file['code']
            response = post_data_file(url=GET_PDF_URL.format(get_pdf_base_url=GET_PDF_BASE_URL, doc_code=doc_code))
            file_path = MINIO_PDF_FILE_PATH.format(entry_id=entry_id, g_no=g_no, filename=filename)

            task = asyncio.create_task(upload_pdf_to_minio("sjdt-ocr", file_path, response.content))
            async_tasks.append(task)
            save_mysql(entry_id=entry_id, g_no=g_no, flag='PENDING', file_name=filename)

    # 等待所有上传minio结束
    await asyncio.gather(*async_tasks)


if __name__ == '__main__':
    check_froms = []
    craw_pending_order(check_froms)
    craw_inspection_order(check_froms)
    get_entry_info(check_froms)
    get_data_document_info(check_froms)
    asyncio.run(get_document_pdf(check_froms))
