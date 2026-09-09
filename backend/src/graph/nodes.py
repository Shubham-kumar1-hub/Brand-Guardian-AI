
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
 
        # Downloading the video from the URL  (using yt-dlp) 
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
 
 
# Node 2 : COMPLIANCE CHECKER 
# Responsible for checking the compliance of the video content against the rules in the knowledge base 
 
def audit_content_node(state: VideoAuditState) -> Dict[str,Any]: 
    ''' 
    Performs RAG based compliance check on the video content 
    ''' 
    logger.info("----[Node: Auditor] quering Knowledge base & LLM") 
    transcript = state.get("transcript","") 
    if not transcript: 
        logger.warning("No Transcript Found. Skipping Compliance Check") 
        return { 
            "final_status" : "FAIL", 
            "final_report" : "No Transcript Found. Compliance Check Skipped", 
        } 
     
    # initializing the Azure OpenAI LLM and Embeddings 
    llm = AzureChatOpenAI( 
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"), 
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"), 
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.1,
    ) 
     
    embeddings = AzureOpenAIEmbeddings( 
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"), 
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"), 
        api_key=os.getenv("AZURE_OPENAI_API_KEY") 
    ) 
 
    # print("=== EMBEDDING CONFIG ===") 
    # print("Endpoint:", os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")) 
    # print("Deployment:", os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")) 
    # print("API Version:", os.getenv("AZURE_OPENAI_API_VERSION")) 
    # print( 
    #     "API Key:", 
    #     os.getenv("AZURE_OPENAI_API_KEY")[:5] + "..." 
    #     if os.getenv("AZURE_OPENAI_API_KEY") 
    #     else "MISSING" 
    # ) 
    # print("========================") 
 
    # print("Testing LangChain embedding...") 
 
    # test_vector = embeddings.embed_query("Hello") 
 
    # print("Embedding SUCCESS!") 
    # print("Vector dimensions:", len(test_vector)) 
     
    vector_store = AzureSearch( 
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"), 
        azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"), 
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"), 
        embedding_function=embeddings.embed_query 
    ) 
 
    # RAG Retrieval 
 
    ocr_text = state.get("ocr_text",[]) 
    query_text = f"{transcript} {''.join(ocr_text)}" 
    docs = vector_store.similarity_search(query_text, k=3)   # retrieve top 3 pages from the document. 
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs]) 
 
    system_prompt = f"""  
            You are a senior brand compliance auditor. 
            OFFICIAL REGULATORY RULES: 
            {retrieved_rules} 
            INSTRUCTIONS:  
            1. Analyze the Transcript and the OCR text below. 
            2. Identify any violation of the rules. 
            3. Return strictly JSON in the following format 
                {{ 
            "compliance_results": [ 
            {{ 
                "category": "Claim Validation", 
                "severity": "CRITICAL", 
                "description": "Explanation of the violation..." 
            }} 
        ], 
        "status": "FAIL", 
        "final_report": "Summary of findings..." 
        }} 
 
        If no violations are found, set "status" to "PASS" and "compliance_results" to []. 
        """ 
 
    user_message = f""" 
                VIDEO_METADATA : {state.get("video_metadata",{})}, 
                TRANSCRIPT : {transcript} 
                ON-SCREEN TEXT (OCR) : {ocr_text} 
                """ 
 
    try: 
        response = llm.invoke([ 
            SystemMessage(content=system_prompt), 
            HumanMessage(content=user_message) 
        ]) 
        content=response.content 
        if "```" in content: 
            content = re.search(r"```(?:json)?(.*?)```",content,re.DOTALL).group(1) 
        audit_data = json.loads(content.strip()) 
        return { 
            "compliance_results" : audit_data.get("compliance_results", []), 
            "final_status"  : audit_data.get("status", "FAIL"), 
            "final_report" : audit_data.get("final_report", "No report generated") 
        } 
 
    except Exception as e: 
        logger.error(f"System error in Auditor Node : {str(e)}") 
        # Logging the raw responses 
        logger.error(f"Raw LLM response : {response.content if 'response' in locals() else 'None'}") 
        return { 
            "errors" : [str(e)], 
            "final_status" : "FAIL" 
        }
