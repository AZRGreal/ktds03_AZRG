import os
import requests
import pandas as pd
import re
from dotenv import load_dotenv

load_dotenv()

# ✅ 이모지 제거 함수
def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # 이모티콘
        u"\U0001F300-\U0001F5FF"  # 기호 및 픽토그램
        u"\U0001F680-\U0001F6FF"  # 교통 및 지도 기호
        u"\U0001F1E0-\U0001F1FF"  # 국기
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# 지하철역 → 좌표 변환
def get_coordinates_from_station(station_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={station_name}+역&key={api_key}"
    response = requests.get(url).json()
    location = response["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# 음식점 + 카페 검색 후 평점 및 리뷰수 기준 정렬
def search_places(lat, lng, radius, api_key):
    types = ["restaurant", "cafe"]
    all_results = []

    for t in types:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": t,
            "language": "ko",
            "key": api_key
        }
        r = requests.get(url, params=params)
        results = r.json().get("results", [])
        for place in results:
            all_results.append({
                "name": place.get("name"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "place_id": place["place_id"],
                "rating": place.get("rating", 0),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "type": t
            })

    # DataFrame 생성 후 정렬
    df = pd.DataFrame(all_results)
    if not df.empty:
        df["user_ratings_total"] = df["user_ratings_total"].fillna(0)
        df["rating"] = df["rating"].fillna(0)
        df = df.sort_values(by=["user_ratings_total", "rating"], ascending=[False, False])

    return df

# CSV 저장
def save_csv_only(df, filename):
    df.to_csv(f"{filename}.csv", index=False, encoding="utf-8-sig")

# 리뷰 추출
def get_place_reviews(place_id, api_key, max_reviews=5):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "review",
        "language": "ko",
        "key": api_key
    }
    response = requests.get(url, params=params).json()
    reviews = response.get("result", {}).get("reviews", [])
    return [r["text"] for r in reviews][:max_reviews]