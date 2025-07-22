#1
# import folium
# from streamlit_folium import st_folium

# def render_map(df, center_lat, center_lng):
#     m = folium.Map(location=[center_lat, center_lng], zoom_start=16)

#     for _, row in df.iterrows():
#         popup_content = f"""
#         <b>{row['name']}</b><br>
#         평점: {row['rating']}<br>
#         리뷰 수: {row['리뷰 수']}
#         """
#         folium.Marker(
#             location=[row["위도"], row["경도"]],
#             popup=popup_content
#         ).add_to(m)

#     return m


#2
# import folium

# def render_map(df, center_lat, center_lng):
#     m = folium.Map(location=[center_lat, center_lng], zoom_start=16)

#     for _, row in df.iterrows():
#         folium.Marker(
#             location=[row['lat'], row['lng']],
#             popup=f"{row['name']}<br>평점: {row['rating']}",
#             tooltip=row['name'],
#             icon=folium.Icon(color="blue", icon="cutlery", prefix="fa")
#         ).add_to(m)

#     return m

#3
import folium

def render_map(df, center_lat, center_lng):
    m = folium.Map(location=[center_lat, center_lng], zoom_start=16)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['lat'], row['lng']],  # 여기 고침
            popup=f"{row['name']}<br>평점: {row['rating']}",
            tooltip=row['name'],
            icon=folium.Icon(color="blue", icon="cutlery", prefix="fa")
        ).add_to(m)

    return m
