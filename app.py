import streamlit as st
import os
import webbrowser
import warnings
warnings.filterwarnings("ignore", message="cmap value too big/small:*")



from utils import (
    get_coordinates_from_station,
    search_places,
    save_csv_only,
    get_place_reviews,
    remove_emojis
)
from azure_blob import upload_to_blob
from openai_utils import summarize_reviews
from map_utils import render_map
from streamlit_folium import st_folium
from save_summary_to_blob import save_summary_to_blob
from video_utils import search_youtube_videos, download_youtube_audio
from speech_utils import transcribe_audio_from_file
from pdf_utils import save_to_pdf

# 환경 변수
google_key = os.getenv("GOOGLE_MAPS_API_KEY")
conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

st.set_page_config(page_title="지하철 맛집 검색기", layout="centered")
st.title("🔍 지하철역 음식점/카페 검색기")

# 초기 세션 상태
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "center_lat" not in st.session_state:
    st.session_state.center_lat = None
if "center_lng" not in st.session_state:
    st.session_state.center_lng = None
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = {}

# Azure 환경 체크
if conn and "AccountName=" in conn and "AccountKey=" in conn:
    st.success("✅ Azure 환경변수 로드 완료")
else:
    st.error("❌ Azure 환경변수 설정 오류")

# 지하철역 검색
station = st.text_input("지하철역을 입력하세요", placeholder="예: 강남역")
radius = 500

if st.button("검색 시작"):
    if not station:
        st.warning("지하철역 이름을 입력하세요.")
    else:
        lat, lng = get_coordinates_from_station(station, google_key)
        df = search_places(lat, lng, radius, google_key)

        if not df.empty:
            df = df.sort_values(by=["user_ratings_total", "rating"], ascending=[False, False])
            st.session_state.search_results = df
            st.session_state.center_lat = lat
            st.session_state.center_lng = lng

            filename_base = f"{station}_search_results"
            save_csv_only(df, filename_base)
            upload_to_blob(f"{filename_base}.csv", f"{filename_base}.csv")
            st.success("📁 CSV 저장 및 Azure 업로드 완료!")
        else:
            st.error("❌ 검색 결과가 없습니다.")

# 검색 결과 및 지도
if st.session_state.search_results is not None:
    df = st.session_state.search_results
    lat = st.session_state.center_lat
    lng = st.session_state.center_lng

    st.success(f"📍 검색 위치: 위도 {lat}, 경도 {lng}")
    st.dataframe(df[["name", "type", "rating", "user_ratings_total"]])
   
    # 지도 출력
    with st.container():
        st.markdown("<h6 style='margin: 5px 0;'>🗺️ 지도에서 위치 보기</h6>", unsafe_allow_html=True)
        map_obj = render_map(df, lat, lng)
        st_folium(map_obj, width=700, height=400, returned_objects=[])

    # 여백 최소화 및 리뷰 타이틀
    with st.container():
        st.markdown("<div style='margin-top: -30px;'></div>", unsafe_allow_html=True)  # 여백 강제 축소
        st.markdown("<h6 style='margin: 5px 0;'>📜 대표 리뷰 및 요약</h6>", unsafe_allow_html=True)

    for idx, row in df.head(3).iterrows():
        st.markdown(f"**{row['name']}** ({row['type']})")
        reviews = get_place_reviews(row["place_id"], google_key)
        if reviews:
            for r in reviews:
                st.markdown(f"- {r}")
            if st.button(f"🤖 GPT 요약 보기 - {row['name']}", key=f"btn_summary_{idx}"):
                summary = summarize_reviews(reviews)
                summary = remove_emojis(summary)
                st.markdown(summary)
                save_summary_to_blob(row["name"], summary)
        else:
            st.markdown("리뷰 없음 😞")
    st.divider()
    st.markdown("### 🔍 상호명으로 유튜브 검색하기")
    name_options = df["name"].tolist()
    selected_name = st.selectbox("검색할 상호명을 선택하세요", name_options, key="youtube_search")
    if st.button("🔗 유튜브에서 검색", key="search_button"):
        query = selected_name.replace(" ", "+")
        youtube_search_url = f"https://www.youtube.com/results?search_query={query}"
        js = f"window.open('{youtube_search_url}')"
        st.components.v1.html(f"""
        <script>
            {js}
        </script>
        """, height=0)
st.divider()
st.markdown("### 🎧 선택된 영상 분석")

st.markdown("아래처럼 GPT가 장점과 단점을 최대 10개까지 요약해줍니다.")
st.markdown("""
✅ **장점 예시**
- 음식이 맛있다는 평이 많음
- 친절한 서비스가 인상적임

❌ **단점 예시**
- 대기 시간이 김
- 가격이 다소 높음
""")

video_url = st.text_input("YouTube 영상 주소를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")
if video_url:
    if st.button("📌 분석 결과 보기"):
        try:
            with st.spinner("📥 YouTube 오디오 다운로드 중..."):
                audio_path = download_youtube_audio(video_url)
                upload_to_blob(audio_path, os.path.basename(audio_path))

            with st.spinner("🗣 Azure Speech로 자막 변환 중..."):
                transcript = transcribe_audio_from_file(audio_path)

            with st.spinner("✍️ 감정 기반 요약 생성 중..."):
                summary = summarize_reviews([transcript])
                summary = remove_emojis(summary)

                # ✅ 페이지에 요약 내용 먼저 표시
                st.markdown("#### 📋 분석 요약 결과")
                st.markdown(summary)

            with st.spinner("📄 PDF 저장 중..."):
                pdf_path = save_to_pdf(summary, filename="youtube_summary.pdf")

            st.success("✅ 분석 완료! 결과를 PDF로 확인하세요.")
            with open(pdf_path, "rb") as f:
                st.download_button("📥 분석 결과 PDF 다운로드", f, file_name=os.path.basename(pdf_path))

        except Exception as e:
            st.error(f"❌ 분석 중 오류 발생: {e}")
else:
    st.info("YouTube 영상 주소를 입력해주세요.")
