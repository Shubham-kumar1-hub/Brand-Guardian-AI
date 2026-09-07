"""
Main Execution Entry Point for Brand Guardian AI.

This file is the "control center" that starts and manages the entire 
compliance audit workflow. It acts as the master switch that:
1. Sets up the audit request
2. Runs the AI workflow
3. Displays the final compliance report
"""

import uuid
import json
import logging
from pprint import pprint
from dotenv import load_dotenv

from backend.src.graph.workflow import create_graph

load_dotenv(override=True)  #  # override=True means .env values take priority over system variables


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Format: timestamp - logger_name - severity - message
    # Example: "2024-01-15 10:30:45 - brand-guardian - INFO - Starting audit"

logger = logging.getLogger("brand-guardian-runner")  # Creates a named logger for this module


def run_cli_simulation():
    """
    Simulates a Video Compliance Audit request.
        
        This function orchestrates the entire audit process:
        - Creates a unique session ID
        - Prepares the video URL and metadata
        - Runs it through the AI workflow
        - Displays the compliance results
    """

    # Generate the session ID
    session_id = str(uuid.uuid4())
    logger.info(f"Starting Audit Session : {session_id}")  # Log to console/file


    # Defining the initial state
    # This dictionary contains all the input data for the workflow
    initial_inputs = {
            # The YouTube video to audit
            "video_url": "https://youtu.be/dT7S75eYhcQ",
            
            # Shortened video ID for easier tracking (first 8 chars of session ID)
            # Example: "vid_ce6c43bb"
            "video_id": f"vid_{session_id[:8]}",
            
            # Empty list that will store compliance violations found
            # Will be populated by the Auditor node
            "compliance_results": [],
            
            # Empty list for any errors during processing
            # Example: ["Download failed", "Transcript unavailable"]
            "errors": []
        }

    print("--------------Initializing Workflow.............")
    print(f"Input Paypload : {json.dumps(initial_inputs, indent=2)}")
    # json.dumps() converts Python dict to formatted JSON string
    # indent=2 makes it readable with 2-space indentation

    app = create_graph()

    try:
        # app.invoke() triggers the LangGraph workflow
        # It passes through: START → Indexer → Auditor → END
        # Returns the final state with all results
        final_state = app.invoke(initial_inputs)
        print("\n-------Workflow execution is complete.......")

        print("\n Compliance Audit Report ==")

        print(f"Video ID : {final_state.get('video_id')}")

        print(f"Status : {final_state.get('final_status')}")

        print("\n [VIOLATIONS DETECTED]")

        # Extract the list of compliance violations
        # Default to empty list if no results
        results = final_state.get('compliance_results', [])

        if results:
            for issue in results:
              # Each issue is a dict with: severity, category, description
              print(f"- [{issue.get('severity')}] {issue.get('category')} : [{issue.get('description')}]")
        else:
            print("No violations detected............")

        # Displays the AI-generated natural language summary    
        print("\n[FINAL SUMMARY]")
        print(final_state.get('final_report'))


    except Exception as e:
        logger.error(f"Workflow Excution has Failed : {str(e)}")
        raise e


if __name__ == "__main__":
    run_cli_simulation() 