import asyncio
from craw_factory import Rsk4CrawFactory


if __name__ == '__main__':
    # 初始化爬虫
    rsk4_craw_fac = Rsk4CrawFactory()
    # 爬取未接单查验单
    rsk4_craw_fac.craw_pending_order()
    # 爬取已接单查验单
    rsk4_craw_fac.craw_inspection_order()
    # 爬取报关单信息，商品项
    rsk4_craw_fac.get_entry_info()
    # 获取报关单申报日期
    rsk4_craw_fac.get_entry_ddate()
    # 获取报关商品
    rsk4_craw_fac.get_data_document_info()
    # 异步上传pdf文件到minio
    asyncio.run(rsk4_craw_fac.get_document_pdf())
