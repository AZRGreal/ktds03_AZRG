# import os
# from dotenv import load_dotenv
# import requests

# load_dotenv()

# endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
# api_key = os.getenv("AZURE_SEARCH_API_KEY")
# index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

# search_query = "*"  # 또는 "카페", "*", "방배", etc

# headers = {
#     "Content-Type": "application/json",
#     "api-key": api_key
# }

# params = {
#     "api-version": "2023-07-01-Preview"
# }

# body = {
#     "search": "*"
# }

# url = f"{endpoint}/indexes/{index_name}/docs/search"

# response = requests.post(url, headers=headers, params=params, json=body)

# if response.status_code == 200:
#     print("✅ 검색 결과:")
#     for doc in response.json()["value"]:
#         print(f"📌 {doc.get('name')} ({doc.get('type')}), 평점: {doc.get('rating')}")
# else:
#     print("❌ 오류 발생:", response.status_code, response.text)

import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

params = {
    "api-version": "2023-07-01-Preview"
}

body = {
    "search": "*",  # 또는 "강남", "카페", 등
    "top": 10
}

url = f"{endpoint}/indexes/{index_name}/docs/search"

response = requests.post(url, headers=headers, params=params, json=body)

if response.status_code == 200:
    print("✅ 문서 샘플 구조:")
    print(json.dumps(response.json()["value"][0], indent=2, ensure_ascii=False))
else:
    print("❌ 오류 발생:", response.status_code, response.text)
