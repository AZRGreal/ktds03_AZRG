# 🚀 지하철 상권 분석기 (Streamlit + Azure)

이 앱은 Google Maps 및 Azure 서비스를 활용해 지하철역 주변 맛집/카페 정보를 검색하고, GPT로 요약하며, Azure Search로 검색 가능한 구조로 저장합니다.

## ✅ 주요 기능
- Google Places API를 통한 상권 데이터 수집
- Azure OpenAI GPT를 이용한 리뷰 요약
- Folium 기반 지도 시각화
- Azure Blob Storage 업로드
- Azure AI Search로 검색 인덱싱

## 🛠️ 구성 파일

| 파일명 | 설명 |
|--------|------|
| `app.py` | Streamlit 웹앱 메인 |
| `utils.py` | 데이터 수집, 저장, 리뷰 수집 등 유틸 함수 |
| `openai_utils.py` | GPT 요약 처리 |
| `map_utils.py` | Folium 지도 생성 |
| `azure_blob.py` | Azure Blob 업로드 기능 |
| `.env` | API 키 및 환경변수 |
| `requirements.txt` | 설치 패키지 목록 |
| `search_setup.py` | Azure Search Index/Indexer/DataSource 자동 생성 스크립트 |

## ⚙️ Azure Search 설정 방법

```bash
python search_setup.py
```

해당 명령을 실행하면 아래 항목이 생성됩니다:
- Search Index (station-index)
- Data Source (Azure Blob 연동)
- Indexer (2시간마다 자동 새로고침)

## 📦 설치

```bash
pip install -r requirements.txt
streamlit run app.py
```