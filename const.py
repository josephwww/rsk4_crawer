from datetime import datetime, timedelta
import pytz
from enum import Enum

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_time_range():
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)

    today_midnight = now - timedelta(hours=12)
    tomorrow_midnight = today_midnight + timedelta(days=1)

    return str(today_midnight.strftime(TIME_FORMAT)), str(tomorrow_midnight.strftime(TIME_FORMAT))


today_midnight, tomorrow_midnight = get_time_range()

TICKET_REFRESH_URL = 'http://10.226.8.11/CustomsInspectionWeb/Ticket/Refresh'

BASE_URL = 'http://10.226.8.11/CustomsInspectionWebApi/Api/{rest}'
TICKET_URL = '{base_url}?ticket={ticket_code}'

# 接口查询最大重试次数
MAX_RETRIES = 3

# 接口重试等待时间
DELAY = 1

# 默认分页页码
DEFAULT_PAGE = 1

# 默认单页条数
PAGE_LIMIT = 200

# 危包查验资质代码，用于未接单判断危化品
HARZ_CERT = 'SJ1'


class HarzFileType(Enum):
    """
    危化品文件类型
    """
    declaration = "80000001"
    label = "80000003"
    instruction = "80000004"


class HarzFileName(Enum):
    """
    危化品单证命名规则
    """
    declaration = "declaration.pdf"
    label = "label.pdf"
    instruction = "instruction.pdf"


# 危化品类型和文件名对应字典
DOC_TYPE_DICT = {
    HarzFileType.declaration.value: HarzFileName.declaration.value,
    HarzFileType.label.value: HarzFileName.label.value,
    HarzFileType.instruction.value: HarzFileName.instruction.value
}


# 货物人工查验接单列表
ORDER_LIST_URL = BASE_URL.format(rest='GoodsWork/ManualWorkHead/List/QueryOrdersPage')
ORDER_LIST_PARAMS = {
    'page': DEFAULT_PAGE,
    'limit': PAGE_LIMIT,
    'orderField': 'DISTRIBUTE_TIME',
    'orderSort': 'desc',
    'wfStatus': 1,
    'confirmFlag': 0,
    'distributeTimeStart': today_midnight,
    'distributeTimeEnd': tomorrow_midnight
}


# 货物人工查验查询已接单列表
CHECK_LIST_URL = BASE_URL.format(rest='DataQuery/GoodsWork/List/QueryPage')
CHECK_LIST_PARAMS = {
    'page': DEFAULT_PAGE,
    'limit': PAGE_LIMIT,
    'orderField': 'MODIFY_TIME',
    'orderSort': 'desc',
    'manChkSiteName': '%皇岗进口危化%',
    'ordersTimeStart': today_midnight,
    'ordersTimeEnd': tomorrow_midnight
}


# 获取报关单商品项列表
ENTRY_LIST_URL = BASE_URL.format(rest='GoodsWork/ManualWorkGoods/List/QueryList')
ENTRY_LIST_PARAMS = {
    'page': DEFAULT_PAGE,
    'limit': 50,  # 一张报关单最多有50个商品项
    'checkFormId': None
}


# 获取报关单申报时间
DDATE_URL = BASE_URL.format(rest='H2018/EntryHead/Info/GetByCheckFormId')
DDATE_PARAMS = {
    'entryId': None,
    'checkFormId': None
}


# 请求查验单证
DOCUMENT_LIST_URL = BASE_URL.format(rest='GoodsWork/ManualWorkGoods/List/DocuQueryList')
DOCUMENT_LIST_PARAMS = {
    'page': 1,
    'limit': 50,
    'checkFormId': None,
    'gNo': None,
}

# 下载PDF
GET_PDF_BASE_URL = BASE_URL.format(rest='H2018/EntryDocu/Info/GetFile')
GET_PDF_URL = "{get_pdf_base_url}&requestData={doc_code}"
MINIO_PDF_FILE_PATH = "data/{entry_id}_{g_no}/{filename}"
