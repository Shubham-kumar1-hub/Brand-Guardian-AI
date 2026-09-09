# FastAPI

import uuid
import logging
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
from typing import List, Optional

# Loading the env file
from dotenv import load_dotenv
load_dotenv(override=True)

# Initializing the telemetry
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

# Importing the workflow graph
from backend.src.graph.workflow import create_graph
compliance_graph = create_graph()

# Configuring the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-server")

# Creating the FastAPI app
app = FastAPI(
    title = "Brand Guardian AI API",
    description = "API for uditing video content against the brand compliance rules",
    version = "1.0.0"
)


# Defining the data Model (pydantic)
class AuditRequest(BaseModel):
    '''
    Defining th expected structure of the request body for the audit endpoint
    '''

    video_url: str

class ComplianceIssue(BaseModel):
    '''
    Defining the structure of a compliance issue
    '''
    category : str
    severity : str
    description : str

class AuditResponse(BaseModel):
    '''
    Defining the expected structure of the response body for the audit endpoint
    '''

    session_id : str
    video_id : str
    status : str
    final_report : str
    compliance_results : List[ComplianceIssue]

# Defining the main endpoint

@app.post("/audit", response_model=AuditResponse)
async def audit_video(request : AuditRequest):
    '''
    Main API endpoint that triggers the audit workflow for a given video URL.
    '''

    session_id = str(uuid.uuid4())
    video_id_short =f"vid{session_id[:8]}"
    logger.info(f"Received Audit request : {request.video_url} (Session : {session_id})")
    # Graphs Inputs
    initial_inputs = {
        "video_url" : request.video_url,
        "video_id" : video_id_short,
        "compliance_results" : [],
        "errors" : []
    }


    try:
        final_state = compliance_graph.invoke(initial_inputs)
        return AuditResponse(
            session_id = session_id,
            video_id = final_state.get("video_id"),
            status = final_state.get("final_status", "UNKNOWN"),
            final_report = final_state.get("final_report", "No Report Generated"),
            compliance_results = final_state.get("compliance_results", [])
        )
    except Exception as e:
        logger.error(f"Audit Failed : {str(e)}")
        raise HTTPException(
            status_code=500,
            detail = f"Workflow Execution Failed : {str(e)}"
        )

# Health Check Endpoint
@app.get("/health")
def health_check():
    '''
    Endpoint to verify if API is working or not
    '''
    return {"status" : "healthy", "service" : "Brand Guardian AI"}