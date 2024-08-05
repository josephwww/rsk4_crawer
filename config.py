import os
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
MYSQL_SZDT_URL = os.getenv("MYSQL_SZDT_URL")
mysql_szdt_engine = create_engine(MYSQL_SZDT_URL, echo=False, pool_pre_ping=True)
SessionMysqlSzdt = sessionmaker(autocommit=False, autoflush=True, bind=mysql_szdt_engine)
session = SessionMysqlSzdt()


class HazardousPdfTask(Base):
    __tablename__ = 'sjdt_hazardous_pdf_task'

    id = Column(CHAR(36), primary_key=True)
    result = Column(Text)
    entry_id = Column(String(18))
    g_no = Column(Integer)
    instruction_status = Column(String(10), default='FAILED')
    label_status = Column(String(10), default='FAILED')
    declaration_status = Column(String(10), default='FAILED')
    llm_status = Column(String(10), default='PENDING')
    yolo_status = Column(String(10), default='PENDING')
    yolo_result = Column(Text)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now)
    instruction_ocr_result = Column(Text)
    label_ocr_result = Column(Text)
    declaration_ocr_result = Column(Text)
    ddate = Column(DateTime)
