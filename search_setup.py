import os
import requests
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
container_name = os.getenv("AZURE_CONTAINER_NAME")
storage_conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# 1. Index 생성
def create_index():
    url = f"{endpoint}/indexes/{index_name}?api-version=2023-07-01-Preview"
    body = {
        "name": index_name,
        "fields": [
            {"name": "name", "type": "Edm.String", "searchable": True, "retrievable": True},
            {"name": "type", "type": "Edm.String", "searchable": True, "retrievable": True},
            {"name": "address", "type": "Edm.String", "retrievable": True},
            {"name": "rating", "type": "Edm.Double", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "review_count", "type": "Edm.Int32", "filterable": True, "sortable": True},
            {"name": "lat", "type": "Edm.Double"},
            {"name": "lng", "type": "Edm.Double"},
            {"name": "place_id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "review_summary", "type": "Edm.String"}
        ]
    }
    res = requests.put(url, headers=headers, json=body)
    print("Index 생성:", res.status_code, res.text)

# 2. Data Source 생성
def create_data_source():
    url = f"{endpoint}/datasources/station-datasource?api-version=2023-07-01-Preview"
    body = {
        "name": "station-datasource",
        "type": "azureblob",
        "credentials": {
            "connectionString": storage_conn
        },
        "container": {
            "name": container_name,
            "query": None
        }
    }
    res = requests.put(url, headers=headers, json=body)
    print("Data Source 생성:", res.status_code, res.text)

# 3. Indexer 생성
def create_indexer():
    url = f"{endpoint}/indexers/station-indexer?api-version=2023-07-01-Preview"
    body = {
        "name": "station-indexer",
        "dataSourceName": "station-datasource",
        "targetIndexName": index_name,
        "schedule": {
            "interval": "PT2H"
        },
        "parameters": {
            "configuration": {
                "parsingMode": "default"
            }
        }
    }
    res = requests.put(url, headers=headers, json=body)
    print("Indexer 생성:", res.status_code, res.text)

if __name__ == "__main__":
    create_index()
    create_data_source()
    create_indexer()