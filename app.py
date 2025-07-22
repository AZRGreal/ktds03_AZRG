import streamlit as st
# from dotenv import load_dotenv
import os
from utils import (
    get_coordinates_from_station,
    search_places,
    save_files_locally,
    get_place_reviews
)
from azure_blob import upload_to_blob
from openai_utils import summarize_reviews
from map_utils import render_map
from streamlit_folium import st_folium
from save_summary_to_blob import save_summary_to_blob

# 환경 변수 로드
# load_dotenv()
google_key = os.getenv("GOOGLE_MAPS_API_KEY")

# 페이지 설정
st.set_page_config(page_title="지하철 주변 맛집 찾기", layout="centered")
st.title("🔍 지하철역 맛집/카페 검색기")

# 세션 상태 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "center_lat" not in st.session_state:
    st.session_state.center_lat = None
if "center_lng" not in st.session_state:
    st.session_state.center_lng = None

# 환경 변수 확인
conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if conn and "AccountName=" in conn and "AccountKey=" in conn:
    st.success("✅ 환경변수 로딩 완료 및 형식 이상 없음")
else:
    st.error("❌ 환경변수 설정 오류")

# 입력 UI
station = st.text_input("지하철역을 입력하세요", placeholder="예: 강남역")
radius = 500

# 검색 실행
if st.button("검색 시작"):
    if not station:
        st.warning("지하철역 이름을 입력하세요.")
    else:
        lat, lng = get_coordinates_from_station(station, google_key)
        df = search_places(lat, lng, radius, google_key)

        if df is not None:
            # 세션에 결과 저장
            st.session_state.search_results = df
            st.session_state.center_lat = lat
            st.session_state.center_lng = lng

            # 파일 저장 및 업로드
            filename_base = f"{station}_search_results"
            save_files_locally(df, filename_base)

            for ext in ["csv", "xlsx", "txt"]:
                upload_to_blob(f"{filename_base}.{ext}", f"{filename_base}.{ext}")

            st.success("📁 검색 결과가 저장되고 Azure에 업로드되었습니다.")
        else:
            st.error("❌ 맛집 검색에 실패했습니다.")

# ✅ 검색 결과가 세션에 저장되어 있을 때만 결과 표시
if st.session_state.search_results is not None:
    df = st.session_state.search_results
    lat = st.session_state.center_lat
    lng = st.session_state.center_lng

    st.success(f"📍 검색 위치: 위도 {lat}, 경도 {lng}")
    st.dataframe(df)

    # ⬇️ 다운로드 버튼
    st.markdown("### ⬇️ 파일 다운로드")
    filename_base = f"{station}_search_results"
    for ext in ["csv", "xlsx", "txt"]:
        file_path = f"{filename_base}.{ext}"
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"{ext.upper()} 파일 다운로드",
                data=f,
                file_name=os.path.basename(file_path),
                mime=(
                    "text/csv" if ext == "csv"
                    else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if ext == "xlsx"
                    else "text/plain"
                )
            )

    # 📝 리뷰 표시
    st.markdown("### 📝 대표 리뷰 보기")
    for i, row in df.head(5).iterrows():
        st.subheader(f"{row['name']} ({row['type']})")
        reviews = get_place_reviews(row["place_id"], google_key)
        if reviews:
            for r in reviews:
                st.markdown(f"- {r}")
        else:
            st.markdown("리뷰 없음 😢")

    # 🤖 GPT 요약
    st.markdown("### 🤖 GPT 장점/단점 요약")
    for i, row in df.head(5).iterrows():
        st.subheader(f"📍 {row['name']}")
        reviews = get_place_reviews(row["place_id"], google_key)
        with st.spinner("GPT가 요약 중입니다..."):
            summary = summarize_reviews(reviews)
        st.markdown(summary)
        st.markdown("---")

        # ✅ 여기서 Blob 저장 호출!
        save_summary_to_blob(row["name"], summary)

    # 지도 시각화
    st.markdown("### 🗺️ 지도에서 위치 보기")
    map_obj = render_map(df, lat, lng)
    st_folium(map_obj, width=700, height=500, returned_objects=[])

