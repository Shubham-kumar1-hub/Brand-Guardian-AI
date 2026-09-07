'''
Connector : Python and Azure video indexer
'''

import os
import requests
import logging
import yt_dlp
import time
from azure.identity import DefaultAzureCredential


logger = logging.getLogger("VideoIndexer")

class VideoIndexerServices:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME", "brand-guardian-pro112")
        self.credential = DefaultAzureCredential()


    # Authenticate and get access token
    def get_access_token(self):
        '''
        Generates an ARM access token
        '''

        try:
            token_object = self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"Failed to get Azure token : {str(e)}")
            raise



    def get_account_token(self, arm_access_token):
        '''
        Exchanges the ARM access token for a Video Indexer account access token
        '''

        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )
        headers = {"Authorization" : f"Bearer {arm_access_token}"}
        payload = {"PermissionType" : "Contributor", "scope" : "Account"}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account token : {response.text}")
        return response.json().get("accessToken")


    # Function to download video from YouTube using yt-dlp
    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        '''
        downloads the youtube video to the local file
        '''
        logger.info(f"Downloading Youtube Video : {url}")
        ydl_opts = {
            'format' : 'best',
            'outtmpl' : output_path,   # output template
            'quiet' : False,
            'no_warning' : False,
            'extractor_args' : {'youtube': {'player_client':['android','web']}},
            'http_headers' : {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                logger.info("Download Complete")
                return output_path
        except Exception as e:
            raise Exception(f"Youtube vido download Failed : {str(e)}")

    # Uploads the video to Azure Video Indexer
    def upload_video(self, video_path, video_name):
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)


        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"

        params = {
            "accessToken" : vi_token,
            "name" : video_name,
            "privacy" : "Private",
            "indexingPreset" : "Default"
        }

        logger.info(f"Uploading file {video_path} to Azure ....")


        # Open the file in binary and stream it on Azure
        with open(video_path, 'rb') as video_file:
            files = {'file' : video_file}
            response =requests.post(api_url, params=params, files=files)
            data = response.json()

            return data.get("id")

        if response.status_code != 200:
            raise Exception(f"Azure Upload Failed : {response.text}")


    def wait_for_processing(self, video_id):
        logger.info(f"Waiting for the video {video_id} to be processed by Azure Video Indexer ....")
        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)

            url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index"

            params = {"accessToken" : vi_token}
            response = requests.get(url, params=params)
            data = response.json()
            state = data.get("state")

            progress = data.get("processingProgress")
            logger.info(
                f"Status : {state} | Progress : {progress}"
            )
            if state == "Processed":
                return data
            elif state == "Failed":
                raise Exception(f"Video Indexing Failed in Azure")
            elif state == "Quarantined":
                raise Exception("Video Quarantined (Copyright/ content Policy Violation)")
            logger.info(f"Status {state} .......waiting30s")
            time.sleep(30)  # Wait for 30 seconds before checking again


    def extract_data(Self, vi_json):
        'Parses the json into our state format'

        transcript_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights",{}).get("transcript",[]):
                transcript_lines.append(insight.get("text"))

        ocr_lines = []
        for v in vi_json.get("videos",[]):
            for insight in v.get("insights",{}).get("ocr",[]):
                ocr_lines.append(insight.get("text"))

        return {
            "transcript" : transcript_lines,
            "ocr_text" : ocr_lines,
            "video_metadata" : {
                "duration" : vi_json.get("summarizedInsights",{}).get("duration"),
                "platform" : "youtube"
            }
        } 
