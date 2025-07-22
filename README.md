# 지하철역 주변 맛집/카페 검색기 + GPT 요약 + Blob 저장

## 📦 기능 요약
- 지하철역 입력 시 주변 음식점/카페 검색
- Google 리뷰 수집 후 Azure OpenAI로 장단점 요약
- 요약 결과를 Azure Blob Storage에 자동 저장
- Streamlit UI + 지도 시각화 + 파일 다운로드

## 🧪 실행 방법
1. `.env` 또는 Azure App Service 환경변수에 아래 값 추가:
   - `GOOGLE_MAPS_API_KEY`
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `AZURE_CONTAINER_NAME`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `AZURE_BLOB_SUMMARY_DIR` (예: `summaries/`)
   - `AZURE_BLOB_FILE_PREFIX` (예: `summary_`)

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 실행:
```bash
streamlit run app.py
```

## 📝 결과 저장 위치
- 요약 파일은 Azure Blob Storage 내 `summaries/summary_{장소명}_{시간}.txt` 형식으로 저장됩니다.
