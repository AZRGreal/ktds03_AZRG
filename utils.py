import os
import requests
import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# 환경변수 불러오기
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 지하철역 → 좌표 변환
def get_coordinates_from_station(station_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={station_name}+거주지&key={api_key}"
    response = requests.get(url).json()
    location = response["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# Google 리뷰 요약 함수
def summarize_reviews(reviews):
    if not reviews:
        return "리뷰 없음"

    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version="2024-02-15-preview"
        )

        messages = [
            {"role": "user", "content": "다음 리뷰들을 한국어로 간단히 요약해줘:\n" + "\n".join(reviews)}
        ]

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            temperature=0.7
        )

        content = response.choices[0].message.content
        if content:
            return content.strip()
        else:
            return "⚠️ GPT 응답이 비어 있음"

    except Exception as e:
        return f"⚠️ GPT 요약 실패: {str(e)}"

# 장소 검색 및 요약
def search_places(lat, lng, radius, api_key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    place_types = ["restaurant", "cafe"]
    all_results = []

    for place_type in place_types:
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": place_type,
            "language": "ko",
            "key": api_key
        }
        response = requests.get(url, params=params).json()
        results = response.get("results", [])

        for place in results:
            place_id = place["place_id"]
            reviews = get_place_reviews(place_id, api_key)
            summary = summarize_reviews(reviews)

            all_results.append({
                "name": place.get("name", ""),
                "type": place_type,
                "address": place.get("vicinity", ""),
                "rating": place.get("rating", 0),
                "review_count": place.get("user_ratings_total", 0),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "place_id": place_id,
                "review_summary": summary
            })

    df = pd.DataFrame(all_results)
    df = df.sort_values(by=["review_count", "rating"], ascending=[False, False]).head(20)
    return df

# Google 리뷰 수집
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

# ✅ CSV만 저장하는 함수
def save_csv_only(df, filename_base="search_results"):
    df.to_csv(f"{filename_base}.csv", index=False, encoding="utf-8-sig")
