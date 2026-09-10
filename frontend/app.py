import streamlit as st
import requests

# FastAPI Backend URL
#http://127.0.0.1:8000
API_URL = "http://127.0.0.1:8000/audit"

st.set_page_config(page_title="Brand Guardian AI", page_icon="🛡️", layout="wide")

st.title("🛡️ Brand Guardian AI")
st.markdown("Automated compliance audits for video content.")

# Input Form
video_url = st.text_input("YouTube Video URL:", placeholder="https://youtu.be/...")

if st.button("Run Compliance Audit"):
    if not video_url:
        st.warning("Please provide a valid video URL.")
    else:
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.video(video_url)
            
        with col2:
            with st.status("Running Audit Workflow... This may take a moment.", expanded=True) as status:
                st.write("Sending request to backend pipeline...")
                try:
                    # Trigger the backend API
                    response = requests.post(API_URL, json={"video_url": video_url})
                    response.raise_for_status()
                    data = response.json()
                    
                    status.update(label="Audit Complete!", state="complete", expanded=False)
                    
                    # Display Metadata
                    st.subheader("Audit Overview")
                    m1, m2 = st.columns(2)
                    m1.metric("Status", data.get("status", "UNKNOWN"))
                    m2.metric("Video ID", data.get("video_id", "N/A"))
                    
                    st.divider()
                    
                    # Display Final Summary
                    st.subheader("Final Report")
                    st.markdown(data.get("final_report", "No summary available."))
                    
                    st.divider()
                    
                    # Display Violations
                    st.subheader("Detected Violations")
                    results = data.get("compliance_results", [])
                    if results:
                        for issue in results:
                            severity = issue.get("severity", "WARNING")
                            category = issue.get("category", "Unknown")
                            desc = issue.get("description", "")
                            
                            if severity.upper() == "CRITICAL":
                                st.error(f"**[{severity}] {category}**: {desc}")
                            else:
                                st.warning(f"**[{severity}] {category}**: {desc}")
                    else:
                        st.success("No compliance violations detected.")

                except requests.exceptions.RequestException as e:
                    status.update(label="Audit Failed", state="error", expanded=True)
                    st.error(f"Connection failed. Ensure the FastAPI server is running. Error: {str(e)}")