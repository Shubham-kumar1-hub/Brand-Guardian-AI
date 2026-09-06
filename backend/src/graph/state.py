import operator
from typing import List, Dict, Annotated, Any, Optional, TypedDict


# Defining the schema for a single compliance check result
class ComplianceIssue(TypedDict):
    category: str
    description: str   # Specific detail about the violation or issue
    severity: str      # CRITICAL | WARNING
    timestamp: Optional[str]


# Defining the gloabl graph state
# This defines the state that get passed around in the agentic workflow

class VideoAuditState(TypedDict):
    '''
    Defining the data schema for langgraph execution content 
    Main container : holds all the information about the audit right from the initial url to the final report 
    '''

    # input parameters
    video_url: str
    video_id: str

    # ingestion and extraction data
    local_file_path: Optional[str]
    video_metadata: Dict[str, Any]  # {"duration": 120, "resolution": "1080p", "format": "mp4"}
    transcript: Optional[str]  # fully extracted speech-to-text
    ocr_text: List[str] # list of text extracted from video frames

    # analyis output
    compliance_results: Annotated[List[ComplianceIssue], operator.add]  # stores the list of all the violations found by AI


    # final report
    final_status : str     # "PASS" | "FAIL"
    final_report : str      # markdown format

    # system observability
    # errors: API timeouts,system level errors, etc
    # list of system level crashes
    errors : Annotated[List[str],operator.add]