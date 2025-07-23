# speech_utils.py

import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")


# 🔊 WAV 파일을 Azure Speech로 전송 → 텍스트 반환
def transcribe_audio_from_file(audio_path: str) -> str:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise Exception("❌ Azure Speech 키 또는 리전 정보가 없습니다. .env 또는 환경 변수 확인 필요")

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = "ko-KR"  # 한국어로 인식

    audio_input = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    print(f"🧠 Azure에 오디오 전송 중: {audio_path}")
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("✅ 음성 인식 성공!")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "❌ 음성을 인식하지 못했습니다."
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        return f"❌ 인식 취소됨: {cancellation.reason} - {cancellation.error_details}"


# import os
# from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer
# from dotenv import load_dotenv

# load_dotenv()

# AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
# AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

# # 🎤 Azure Speech → 텍스트 변환 함수
# def transcribe_audio_from_file(audio_path):
#     try:
#         speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
#         audio_config = AudioConfig(filename=audio_path)

#         speech_recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
#         result = speech_recognizer.recognize_once()

#         if result.reason.name == "RecognizedSpeech":
#             return result.text
#         else:
#             return f"❌ 음성 인식 실패: {result.reason}"
#     except Exception as e:
#         return f"❌ 예외 발생: {e}"

