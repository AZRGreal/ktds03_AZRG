import folium
from folium.plugins import MarkerCluster
import pandas as pd

# 📍 지도 렌더링 함수
def render_map(df, center_lat, center_lng):
    """
    중심 좌표를 기준으로 마커 클러스터링된 Folium 지도 객체를 생성합니다.
    """
    # 지도 초기화
    m = folium.Map(location=[center_lat, center_lng], zoom_start=16)

    # 클러스터링 레이어 생성
    marker_cluster = MarkerCluster().add_to(m)

    # 데이터프레임 순회하며 마커 추가
    for _, row in df.iterrows():
        name = row.get("name", "이름 없음")
        lat = row.get("lat")
        lng = row.get("lng")
        place_type = row.get("type", "분류 없음")

        # 좌표 유효성 확인
        if pd.notnull(lat) and pd.notnull(lng):
            popup_text = f"{name} ({place_type})"
            folium.Marker(
                location=[lat, lng],
                popup=popup_text,
                icon=folium.Icon(color="blue", icon="cutlery", prefix="fa")
            ).add_to(marker_cluster)

    return m
