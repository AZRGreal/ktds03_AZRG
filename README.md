✅ 1. 배경 (Background)
이 앱은 지하철역 근처 음식점/카페를 검색하고, 해당 장소의 Google 리뷰 요약 및 유튜브 영상 기반 분석을 통해 맛집 정보를 시각적으로 제공하는 종합 도구입니다.
또한 Azure의 다양한 AI 서비스를 연동하여 리뷰 분석, 음성 인식, PDF 저장까지 자동화된 워크플로우를 제공합니다.

🎯 2. 목적 (Purpose)
지하철역 기반 장소 검색 (음식점/카페)

Google 리뷰 분석 및 GPT 요약

유튜브 영상 입력 → 오디오 다운로드 → 자막 변환 → GPT 요약

요약 결과를 PDF로 저장 및 다운로드

Azure Blob에 파일 업로드 자동화

🌐 3. 사용 API (Used APIs)
카테고리	API/서비스명	설명
지도 검색	Google Maps Geocoding API	지하철역명 → 위도/경도 변환,
장소 검색	Google Places API	음식점/카페 장소 목록 가져오기,
리뷰 정보	Google Place Details API	각 장소의 리뷰 가져오기,
영상 다운로드	pytube	유튜브 영상 오디오 추출,
음성 → 자막	Azure Speech to Text API	유튜브 오디오 → 텍스트 자막 변환,
텍스트 요약	Azure OpenAI GPT	리뷰 또는 자막 내용 요약

☁️ 4. AZURE 활용 도구
도구명	역할
Azure Blob Storage	분석 결과 및 오디오/CSV 파일 업로드 저장소
Azure Speech Service	유튜브 오디오 → 텍스트 변환
Azure OpenAI (GPT)	리뷰/자막 → 감정 기반 요약 생성
(선택) Azure Functions	반복작업 자동화 가능 (현재 코드엔 없음)

👍 5. 장점 (Strengths)
한 페이지에서 통합된 워크플로우
→ 장소 검색 → 리뷰 분석 → 유튜브 분석 → 요약/PDF까지 완료

Azure 기반의 자동화된 AI 분석
→ 음성 텍스트 변환과 요약이 자연스럽게 연결됨

Streamlit 인터페이스
→ 사용자 친화적이며 직관적인 UI 제공

Google + Azure 결합
→ Google Maps 데이터 + Azure AI 분석이라는 강력한 조합

PDF 다운로드 및 Azure 업로드
→ 결과 저장성과 공유 기능 제공

👎 6. 단점 (Limitations)
API Key/환경 변수 의존도 높음
→ Google과 Azure 환경 변수 미설정 시 즉시 오류 발생

실시간 YouTube 영상 자동 검색 기능 없음
→ GPT 기반 추천은 없고, 사용자가 직접 유튜브 링크 입력해야 함

에러 처리 부족
→ 예외는 있지만 API 응답 문제나 네트워크 실패 시 사용자 친화적 메시지가 부족할 수 있음

로컬에서만 실행됨 (현재 상태 기준)
→ 배포되지 않았다면 실제 사용자가 접근하기 어려움 (Streamlit Cloud, Azure Web App 필요)

속도 문제 가능성
→ 유튜브 다운로드 + 음성 분석 + 요약까지 한 번에 수행하므로, 성능에 따라 지연 발생

📦 요약 정리
항목	설명
앱 유형	맛집 검색 및 리뷰/영상 분석 앱
주요 입력	지하철역 이름, 유튜브 영상 링크
주요 출력	장소 리스트, 요약 리뷰, 요약 PDF
사용 기술	Streamlit, Google API, Azure OpenAI, Azure Speech, Blob Storage
PDF 생성	FPDF + 나눔글꼴 사용

