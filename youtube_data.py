# youtube_data.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def get_video_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def get_title_and_description(html):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("meta", property="og:title")
    desc_tag = soup.find("meta", property="og:description")
    title = title_tag["content"] if title_tag else ""
    desc = desc_tag["content"] if desc_tag else ""
    return title, desc

def get_comments(video_id, max_comments=500):
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("YOUTUBE_API_KEY 환경변수가 설정되지 않았습니다.")
        return []

    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat='plainText'
        ).execute()

        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if len(comments) >= max_comments:
                break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return "\n".join([entry['text'] for entry in transcript])
    except Exception:
        return ""

def get_video_data(url, max_comments=500):
    video_id = extract_video_id(url)
    if not video_id:
        return None, None, None, None

    html = get_video_page(url)
    if not html:
        return None, None, None, None

    title, desc = get_title_and_description(html)
    transcript = get_transcript(video_id)
    comments = get_comments(video_id, max_comments=max_comments)

    return title, desc, transcript, comments
