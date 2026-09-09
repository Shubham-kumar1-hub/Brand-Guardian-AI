import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor


# Creating a logger for telemetry
logger = logging.getLogger("brand-guardian-telemetry")

def setup_telemetry():
    '''
    Initializes Azure Monitor OpenTelemetry
    Tracks: HTTP requests, database queries, errors, performances metrics, etc.
    Sends this data to azure monitor
    
    It auto captures every API request
    No need to manually log each endpoint 
    '''


    # Retrieving the connection string from environment variables
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    # Checking if the connection string is available
    if not connection_string:
        logger.warning("Azure Monitor connection string is not set. Telemetry will not be sent.")
        return

    # Configuring Azure Monitor OpenTelemetry
    try:
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name="brand-guardian-telemetry"
        )

        logger.info("Azure Monitor OpenTelemetry configured successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Monitor OpenTelemetry: {str(e)}")