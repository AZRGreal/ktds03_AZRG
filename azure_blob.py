from azure.storage.blob import BlobServiceClient
import os

def upload_to_blob(local_file, blob_name):
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("AZURE_CONTAINER_NAME")

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)

    with open(local_file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
