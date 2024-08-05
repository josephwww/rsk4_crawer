from minio import Minio
from minio.error import S3Error
import io
import os

    
def get_minio_client():
    minio_client = Minio(
        os.getenv("MINIO_ADDRESS"),
        access_key="JaDcmljOz2aqIFralr39",
        secret_key="zJRoNQrAOYuClCtTtSLbciK9M3FodP0AxWgwEcOz",
        secure=False
    )
    return minio_client


async def upload_pdf_to_minio(bucket_name, file_path, file_data):
    minio_client = get_minio_client()
    file_length = len(file_data)

    # 上传文件
    try:
        minio_client.put_object(bucket_name, file_path, io.BytesIO(file_data), file_length)
    except S3Error as e:
        print("error: ", e)
