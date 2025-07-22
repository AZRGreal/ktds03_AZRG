import streamlit as st
import os
import requests
from utils import (
    get_coordinates_from_station,
    search_places,
    save_csv_only,  # ✅ CSV만 저장 함수
    get_place_reviews
)
from azure_blob import upload_to_blob
from openai_utils import summarize_reviews
from map_utils import render_map
from streamlit_folium import st_folium
from save_summary_to_blob import save_summary_to_blob

# ✅ Google 리뷰 캐싱
@st.cache_data(show_spinner=False)
def get_cached_reviews(place_id, api_key, max_reviews=5):
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

# ✅ 환경 변수 로드
google_key = os.getenv("GOOGLE_MAPS_API_KEY")

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="지하철 주부 맛집 찾기", layout="centered")
st.title("🔍 지하철역 맛집/카페 검색기")

# ✅ 세션 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "center_lat" not in st.session_state:
    st.session_state.center_lat = None
if "center_lng" not in st.session_state:
    st.session_state.center_lng = None

# ✅ Azure 환경 변수 확인
conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if conn and "AccountName=" in conn and "AccountKey=" in conn:
    st.success("✅ Azure 환경변수 로드 완료")
else:
    st.error("❌ Azure 환경변수 설정 오류")

# ✅ 검색 UI
station = st.text_input("지하철역을 입력하세요", placeholder="예: 강남역")
radius = 500

# ✅ 검색 버튼
if st.button("검색 시작"):
    if not station:
        st.warning("지하철역 이름을 입력하세요.")
    else:
        lat, lng = get_coordinates_from_station(station, google_key)
        df = search_places(lat, lng, radius, google_key)

        if df is not None:
            st.session_state.search_results = df
            st.session_state.center_lat = lat
            st.session_state.center_lng = lng

            filename_base = f"{station}_search_results"

            # ✅ CSV 저장 및 업로드
            save_csv_only(df, filename_base)
            upload_to_blob(f"{filename_base}.csv", f"{filename_base}.csv")

            st.success("📁 CSV 저장 및 Azure 업로드 완료!")
        else:
            st.error("❌ 검색 결과가 없습니다.")

# ✅ 검색 결과 출력
if st.session_state.search_results is not None:
    df = st.session_state.search_results
    lat = st.session_state.center_lat
    lng = st.session_state.center_lng

    st.success(f"📍 검색 위치: 위도 {lat}, 경도 {lng}")
    st.dataframe(df)

    # ✅ 대표 리뷰 캐싱
    cached_reviews = {
        row["place_id"]: get_cached_reviews(row["place_id"], google_key)
        for _, row in df.head(10).iterrows()
    }

    # ✅ 대표 리뷰 표시
    st.markdown("### 📜 대표 리뷰 보기")
    for _, row in df.head(10).iterrows():
        st.subheader(f"{row['name']} ({row['type']})")
        reviews = cached_reviews.get(row["place_id"], [])
        if reviews:
            for r in reviews[:3]:
                st.markdown(f"- {r}")
        else:
            st.markdown("리뷰 없음 😞")

    # ✅ GPT 요약
    st.markdown("### 🧐 GPT 장점/단점 요약")
    for _, row in df.head(3).iterrows():
        st.subheader(f"📍 {row['name']}")
        reviews = cached_reviews.get(row["place_id"], [])
        with st.spinner("GPT가 요약 중입니다..."):
            summary = summarize_reviews(reviews)
        st.markdown(summary)
        st.markdown("---")
        save_summary_to_blob(row["name"], summary)

    # ✅ 지도 표시
    st.markdown("### 🗌 지도에서 위치 보기")
    map_obj = render_map(df, lat, lng)
    st_folium(map_obj, width=700, height=500, returned_objects=[])
