import json
import os
import logging
import re
from typing import Any, Dict, List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Importing state schema
from backend.src.graph.state import VideoAuditState, ComplianceIssue

# Importing Services
from backend.src.services.video_indexer import VideoIndexerServices

# Configure the logger
logger = logging.getLogger("brand_guardian_ai")
logging.basicConfig(level=logging.INFO)


# Node 1 : INDEXER
# Responsible for converting the video to text and extracting metadata

def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    '''
    Download the youtube videos form the url
    Uploads to the Azure Video Indexer
    extracts the insights
    '''
    video_url = state.get("video_url")
    video_id_input = state.get("video_id","vid_demo")

    logger.info(f"----[Node: Indexer] Processing : {video_url}")

    local_filename = "temp_audit_video.mp4"

    try:
        vi_service = VideoIndexerServices()

        # Downloading the video from the URL
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            raise Exception("Please Provide a valid youtube video url")

        # Uploading the video to Azure Video Indexer
        azure_video_id = vi_service.upload_video(local_path, video_name=video_id_input)
        logger.info(f"Upload Success. Azure ID : {azure_video_id}")

        # clean up the local file after upload
        if os.path.exists(local_path):
            os.remove(local_path)

        # waiting for the video to be processed
        raw_insights = vi_service.wait_for_processing(azure_video_id)

        # Extracting the insights from the raw data
        clean_data = vi_service.extract_data(raw_insights)
        logger.info("----[Node: Indexer] Extraction Complete ----")
        return clean_data
    except Exception as e:
        logger.error(f"Video Indexer Failed: {e}")
        return {
            "errors" : [str(e)],
            "final_status" : "FAIL",
            "transcript" : "",
            "ocr_text" : []
        }