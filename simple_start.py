import os
import json
from googleapiclient.discovery import build
from pytube import YouTube

from GetSysPath import *
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv(".env")

class YouTubeDataHunter:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.video_overall_file = 'videos_info.json'

    def get_videos_info_from_channels(self, channel_ids, specific_date):
        videos_content = []
        for channel_id in channel_ids:
            print(f"Searching for videos from channel ID: {channel_id}")
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                publishedAfter=specific_date,
                maxResults=25,
                type='video',
                order='date'
            )
            response = request.execute()

            for item in response.get('items', []):
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_description = item['snippet']['description']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_context = self.download_all_captions([video_url])

                videos_content.append({
                    "id": video_id,
                    "title": video_title,
                    "description": video_description,
                    "url": video_url,
                    "video_context": video_context
                })

        return videos_content

    def save_videos_to_json(self, videos_content):
        try:
            with open(self.video_overall_file, 'w', encoding='utf-8') as json_file:
                json.dump(videos_content, json_file, ensure_ascii=False, indent=4)
            print(f"Video information has been saved to '{self.video_overall_file}'.")
        except Exception as e:
            print("An error occurred while saving the JSON file:\n", e)

    def read_videos_from_json(self):
        video_urls = []
        try:
            with open(self.video_overall_file, 'r', encoding='utf-8') as json_file:
                videos_info = json.load(json_file)

            for video in videos_info:
                video_urls.append(video['url'])    
            
            return video_urls
        
        except Exception as e:
            print(f"Error reading the JSON file: {e}")
            return []

    def download_all_captions(self, video_urls):

        for url in video_urls:
            yt = YouTube(url)
            
            # Check if there are any captions available
            if yt.captions:
                for caption in yt.captions.all():
                    try:
                        caption_text = caption.generate_srt_captions()
                        print(f"--- Captions ({caption.language_code}) ---")
                        print(caption_text)
                    except Exception as e:
                        print(f"Error downloading captions ({caption.language_code}): {e}")
            else:
                print("No captions available for this video.")
            print("\n")


if __name__ == "__main__":

    # 三立 youtube 頻道 ID
    channel_ids = ["UCIU8ha-NHmLjtUwU7dFiXUA", "UC2TuODJhC03pLgd6MpWP0iw", "UCPARDnYdJQBJID-qyefVKcw",
                   "UC2hslcZZSHF1u_KW4LPrRPA", "UCoNYj9OFHZn3ACmmeRCPwbA"]

    three_days_ago = datetime.now() - timedelta(days=1)
    specific_date = three_days_ago.isoformat("T") + "Z"

    hunter = YouTubeDataHunter(os.getenv("YOUTUBE_API_KEY"))

    # videos_content = hunter.get_videos_info_from_channels(channel_ids, specific_date)

    # hunter.save_videos_to_json(videos_content)

    hunter.download_all_captions(hunter.read_videos_from_json())