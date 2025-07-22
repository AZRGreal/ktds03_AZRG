import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime

def save_summary_to_blob(place_name: str, summary: str) -> str:
    """요약 텍스트를 Azure Blob Storage에 저장합니다."""
    try:
        # 환경 변수 불러오기
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_CONTAINER_NAME")
        blob_dir = os.getenv("AZURE_BLOB_SUMMARY_DIR", "summaries/")
        prefix = os.getenv("AZURE_BLOB_FILE_PREFIX", "summary_")

        # 파일 이름 구성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_place_name = place_name.replace(" ", "_").replace("/", "_")
        blob_name = f"{blob_dir}{prefix}{safe_place_name}_{timestamp}.txt"

        # Blob 클라이언트 설정
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_service.get_container_client(container_name)

        # Blob에 내용 업로드
        container_client.upload_blob(name=blob_name, data=summary, overwrite=True)

        print(f"✅ Summary saved to blob: {blob_name}")
        return blob_name
    except Exception as e:
        print(f"❌ Failed to save summary to blob: {e}")
        return ""
