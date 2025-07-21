import requests
import pandas as pd

# 지하철역 → 좌표 변환
def get_coordinates_from_station(station_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={station_name}+지하철역&key={api_key}"
    response = requests.get(url).json()
    location = response["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# 음식점/카페 검색 (place_id 포함)
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
            all_results.append({
                "이름": place["name"],
                "유형": place_type,
                "주소": place.get("vicinity", ""),
                "평점": place.get("rating", 0),
                "리뷰 수": place.get("user_ratings_total", 0),
                "위도": place["geometry"]["location"]["lat"],
                "경도": place["geometry"]["location"]["lng"],
                "place_id": place["place_id"]
            })

    df = pd.DataFrame(all_results)
    df = df.sort_values(by=["리뷰 수", "평점"], ascending=[False, False]).head(20)
    return df

# 로컬 파일 저장
def save_files_locally(df, filename_base="search_results"):
    df.to_csv(f"{filename_base}.csv", index=False)
    df.to_excel(f"{filename_base}.xlsx", index=False)
    with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
        f.write(df.to_string(index=False))

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
