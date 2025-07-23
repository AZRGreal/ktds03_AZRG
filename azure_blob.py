# azure_blob.py

import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "files")  # 기본값 "files"

def upload_to_blob(local_file_path, blob_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

        # 컨테이너가 없으면 생성
        if not container_client.exists():
            container_client.create_container()

        with open(local_file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)

        print(f"✅ {blob_name} 업로드 성공")
        return True
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
        return False
