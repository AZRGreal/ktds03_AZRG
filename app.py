import streamlit as st
import os
import warnings
from youtube_data import get_video_data
from openai_utils import summarize_pros_cons, summarize_reviews, safe_text
from utils import (
    get_coordinates_from_station,
    search_places,
    save_csv_only,
    get_place_reviews,
    remove_emojis
)
from azure_blob import upload_to_blob
from map_utils import render_map
from streamlit_folium import st_folium
from save_summary_to_blob import save_summary_to_blob

warnings.filterwarnings("ignore", message="cmap value too big/small:*")

# 환경 변수
google_key = os.getenv("GOOGLE_MAPS_API_KEY")
conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

st.set_page_config(page_title="지하철 맛집 검색기", layout="centered")
st.title("🔍 지하철역 주변 음식점/카페 검색기")

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

    # 지도 타이틀
    st.markdown(
        """
        <div style='margin:0;padding:0;line-height:1;'>
            <h6 style='margin:0;padding:0;line-height:1;'>🗺️ 지도에서 위치 보기</h6>
        </div>
        """, unsafe_allow_html=True
    )
    # 지도 표시
    map_obj = render_map(df, lat, lng)
    st_folium(map_obj, width=700, height=400, returned_objects=[])
    # 지도 바로 아래에 리뷰 타이틀 붙이기
    st.markdown(
        """
        <div style='margin:0;padding:0;line-height:1;margin-top:-30px;'>
            <h6 style='margin:0;padding:0;line-height:1;margin-bottom:0px;margin-top:0px;'>📜 대표 리뷰 및 요약</h6>
        </div>
        """, unsafe_allow_html=True
    )

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

    # 상호명으로 유튜브 검색
    st.markdown("<hr style='margin-top:8px;margin-bottom:4px;'>", unsafe_allow_html=True)
    st.markdown("### 🔍 상호명으로 유튜브 검색하기")
    name_options = df["name"].tolist()
    selected_name = st.selectbox("검색할 상호명을 선택하세요", name_options, key="youtube_search")
    if st.button("🔗 유튜브에서 검색", key="search_button"):
        query = selected_name.replace(" ", "+")
        youtube_search_url = f"https://www.youtube.com/results?search_query={query}"
        js = f"window.open('{youtube_search_url}')"
        st.components.v1.html(f"""
        <script>{js}</script>
        """, height=0)

# 새 기능: YouTube 영상 URL 분석기 (댓글 500개까지)
st.markdown("<hr style='margin-top:16px;margin-bottom:4px;'>", unsafe_allow_html=True)
st.markdown("### 🔍 YouTube 영상 URL 기반 분석기")
st.markdown("영상의 제목, 설명, 자막, 댓글(최대 500개)을 기반으로 GPT가 장단점을 요약해줍니다.")

video_url = st.text_input("🎬 분석할 YouTube 영상 URL을 입력하세요", key="yt_summary_url")

if video_url:
    if st.button("🧠 GPT 요약 시작", key="btn_summarize_url"):
        with st.spinner("📥 영상 정보 수집 중..."):
            title, desc, transcript, comments = get_video_data(video_url, max_comments=500)

        st.write(f"제목 길이: {len(title)}")
        st.write(f"설명 길이: {len(desc)}")
        st.write(f"자막 길이: {len(transcript)}")
        st.write(f"댓글 개수: {len(comments)}")

        if not any([title, desc, transcript, comments]):
            st.error("❌ 영상 정보를 불러오지 못했습니다.")
        else:
            st.success("✅ 영상 정보 수집 완료!")
            st.markdown(f"**📌 제목:** {title}")
            st.markdown(f"**📝 설명:** {desc}")

            comments_text = "\n".join(comments[:500])
            combined = "\n".join([title, desc, transcript, comments_text])
            cleaned = safe_text(combined)

            with st.spinner("🤖 GPT로 장·단점 요약 중..."):
                summary = summarize_pros_cons(cleaned)

            st.markdown("### 🎯 분석 결과")
            st.text_area("GPT 요약", summary, height=800)
