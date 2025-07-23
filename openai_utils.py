import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# 감정 기반 리뷰 요약 함수 (장점/단점 최대 10개)
def summarize_reviews(reviews):
    if not reviews:
        return "리뷰 없음"

    try:
        text = "\n".join(reviews)

        # 텍스트 길이 제한
        if len(text) > 4000:
            text = text[:4000] + "\n...(이후 생략)"

        prompt = f"""
당신은 감성 분석과 요약에 능한 GPT AI입니다.
다음 리뷰들을 분석해 장점과 단점을 최대 10개씩 bullet point 형식으로 정리해주세요.
리뷰는 다양한 사용자의 피드백이며, 음식점이나 카페에 대한 정보일 수 있습니다.

[리뷰 내용]
{text}

[출력 형식 예시]
✅ 장점:
- 맛이 좋다는 평가가 많음
- 친절한 서비스가 인상적임
...

❌ 단점:
- 대기 시간이 김
- 가격이 다소 높음
...

지금 분석을 시작하세요.
"""

        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "너는 한국어 감성 리뷰 분석 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )

        if response.choices and response.choices[0].message:
            return response.choices[0].message.content.strip()
        else:
            return "❌ GPT 응답이 비어 있습니다."

    except Exception as e:
        print(f"❌ GPT 요약 중 오류: {e}")
        return f"❌ GPT 요약 중 오류 발생: {e}"
