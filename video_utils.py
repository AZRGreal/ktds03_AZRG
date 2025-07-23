import os
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
FFMPEG_PATH = os.getenv("VIDEO_FFMPEG_PATH", "C:/ffmpeg/bin/ffmpeg.exe")

# 🔍 유튜브 영상 검색 (조회수 기준 정렬, 쇼츠 제외)
def search_youtube_videos(query, max_results=3):
    try:
        import requests
        from isodate import parse_duration

        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": 10
        }
        response = requests.get(search_url, params=search_params)
        search_resp = response.json()

        video_ids = [item["id"]["videoId"] for item in search_resp.get("items", []) if "videoId" in item["id"]]

        if not video_ids:
            return []

        video_url = "https://www.googleapis.com/youtube/v3/videos"
        stats_params = {
            "key": YOUTUBE_API_KEY,
            "id": ",".join(video_ids),
            "part": "snippet,contentDetails,statistics"
        }
        stats_resp = requests.get(video_url, params=stats_params).json()

        results = []
        for v in stats_resp.get("items", []):
            duration_iso = v["contentDetails"]["duration"]
            duration = parse_duration(duration_iso).total_seconds() / 60

            if duration >= 2:
                results.append({
                    "title": v["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={v['id']}",
                    "views": int(v["statistics"].get("viewCount", 0)),
                    "duration": f"{duration:.1f}분"
                })

        return sorted(results, key=lambda x: x["views"], reverse=True)[:max_results]
    except Exception as e:
        print("❌ 유튜브 검색 실패:", e)
        return []

# 🔉 유튜브에서 오디오(mp3/wav)만 다운로드
def download_youtube_audio(youtube_url, output_dir="downloads"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'ffmpeg_location': FFMPEG_PATH,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_filename = os.path.join(output_dir, f"{info['id']}.wav")
            if os.path.exists(audio_filename):
                print(f"✅ 오디오 다운로드 완료: {audio_filename}")
                return audio_filename
            else:
                raise FileNotFoundError("WAV 파일 생성 실패")
    except Exception as e:
        print(f"❌ 오디오 다운로드 실패: {e}")
        return None

# 🎥 전체 영상 다운로드 (사용하지 않음)
def download_youtube_video(youtube_url, output_dir="downloads"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'ffmpeg_location': FFMPEG_PATH,
            'quiet': True,
            'merge_output_format': 'mp4'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            filename = os.path.join(output_dir, f"{info['id']}.mp4")
            return filename if os.path.exists(filename) else None
    except Exception as e:
        print(f"❌ 유튜브 영상 다운로드 실패: {e}")
        return None

# 🔊 ffmpeg로 오디오 추출 (.wav)
def extract_audio_from_video(video_path):
    try:
        audio_path = video_path.replace(".mp4", ".wav")
        command = f'"{FFMPEG_PATH}" -y -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'
        result = os.system(command)
        if result != 0:
            raise RuntimeError("FFmpeg 명령 실행 실패")
        return audio_path
    except Exception as e:
        print(f"❌ 오디오 추출 실패: {e}")
        return None
