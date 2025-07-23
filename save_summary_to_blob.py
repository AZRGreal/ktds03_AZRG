import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

# Azure Storage 연결 문자열
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "summaries")

# GPT 요약 결과를 Blob에 저장
def save_summary_to_blob(place_name, summary_text):
    try:
        blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service.get_container_client(CONTAINER_NAME)

        # 컨테이너 없으면 생성
        if not container_client.exists():
            container_client.create_container()

        blob_name = f"summaries/{place_name}.txt"
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(summary_text, overwrite=True)
        print(f"✅ 요약 저장 완료: {blob_name}")
    except Exception as e:
        print(f"❌ 요약 저장 실패: {e}")
