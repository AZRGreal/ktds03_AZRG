import os
from dotenv import load_dotenv
from openai import AzureOpenAI



# ✅ .env 명시적으로 로드
load_dotenv(dotenv_path=".env")

# ✅ 환경 변수 출력 확인
print("🔎 AZURE_OPENAI_API_KEY =", os.getenv("AZURE_OPENAI_API_KEY")[:10])
print("🔎 AZURE_OPENAI_ENDPOINT =", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("🔎 AZURE_OPENAI_DEPLOYMENT =", os.getenv("AZURE_OPENAI_DEPLOYMENT"))

# ✅ Azure OpenAI 클라이언트 생성
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",  # ✅ 최신 API 버전으로 수정!
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def summarize_reviews(reviews):
    if not reviews:
        return "리뷰 없음"

    prompt = f"""
다음은 음식점에 대한 실제 사용자 리뷰입니다. 이 리뷰들을 바탕으로 장점(👍)과 단점(👎)을 bullet point 형식으로 요약해 주세요.

리뷰 목록:
{chr(10).join(f"- {r}" for r in reviews)}

요약:
"""

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 요약 실패: {str(e)}"
