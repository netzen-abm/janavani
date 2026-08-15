import streamlit as st
import requests
import os
import pandas as pd

# Set up secure, non-persistent browser framework configurations
st.set_page_config(
    page_title="JanaVani — Internal Core Admin Console",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 JanaVani System Analytics Portal")
st.subheader("Privacy-by-Default Infrastructure Monitoring Terminal")

# Read interface access variables from local system host profiles securely
API_GATEWAY_URL = os.getenv("JANAVANI_INTERNAL_API_URL", "http://ai-agent-service:8000/api/v1/agent/metrics")
INTERFACE_TOKEN = os.getenv("ADMIN_INTERFACE_SECRET_TOKEN", "web-mvp-token-abc")

headers = {
    "X-Janavani-Interface-Token": INTERFACE_TOKEN
}

try:
    # Query the isolated metrics API route endpoint
    response = requests.get(API_GATEWAY_URL, headers=headers, timeout=10)
    
    if response.status_code == 200:
        raw_text_lines = response.text.split("\n")
        total_count = 0
        
        # Parse standard Prometheus text line configurations manually for display
        for line in raw_text_lines:
            if line.startswith("janavani_total_documents_generated_globally"):
                total_count = int(line.split()[-1])
                
        # Render clean, highly readable visual summary layout cards inside dashboard memory
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Official Documents Generated (Global)", value=total_count)
        with col2:
            st.metric(label="Telemetry Storage Status", value="ACTIVE (In-Memory Only)")
            
        # Provide sample tabular representation framework grids for diagnostics
        st.markdown("### 📊 Platform Daily Aggregate Throughput Trends")
        mock_trends_data = pd.DataFrame({
            "Date Dimension": ["2026-08-13", "2026-08-14", "2026-08-15"],
            "Document Type Cluster": ["RTI Request", "Complaint", "Representation"],
            "Aggregated Throughput Count": [12, 45, 29]
        })
        st.dataframe(mock_trends_data, use_container_width=True)
        
    else:
        st.error(f"Failed to pull active metric grids. Gateway Status Code: {response.status_code}")
        
except Exception as error_trace:
    st.error(f"Metrics collection cluster currently unreachable. Trace: {str(error_trace)}")

# ---------------------------

import streamlit as st
import requests
import os
import pandas as pd

st.set_page_config(
    page_title="JanaVani — Internal Core Admin Console",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 JanaVani System Analytics Portal")
st.subheader("Privacy-by-Default Infrastructure Monitoring Terminal")

API_GATEWAY_URL = os.getenv("JANAVANI_INTERNAL_API_URL", "http://ai-agent-service:8000/api/v1/agent/metrics")
FEEDBACK_BASE_URL = os.getenv("JANAVANI_INTERNAL_FEEDBACK_URL", "http://ai-agent-service:8000/api/v1/feedback/summary")
INTERFACE_TOKEN = os.getenv("ADMIN_INTERFACE_SECRET_TOKEN", "web-mvp-token-abc")

headers = {
    "X-Janavani-Interface-Token": INTERFACE_TOKEN
}

# --- Block 1: Performance Matrix Queries ---
try:
    response = requests.get(API_GATEWAY_URL, headers=headers, timeout=10)
    if response.status_code == 200:
        raw_text_lines = response.text.split("\n")
        total_count = 0
        for line in raw_text_lines:
            if line.startswith("janavani_total_documents_generated_globally"):
                total_count = int(line.split()[-1])
                
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Official Documents Generated (Global)", value=total_count)
        with col2:
            st.metric(label="Telemetry Storage Status", value="ACTIVE (In-Memory Only)")
except Exception as error_trace:
    st.error(f"Metrics collection cluster currently unreachable: {str(error_trace)}")

# --- Block 2: Municipal Office Performance Dashboard ---
st.markdown("---")
st.markdown("### 🏛️ Municipal Office Citizen Satisfaction Tracking Board")

target_office = st.selectbox("Select Target Center to Inspect Accountabilities:", ["KL-TVM-01", "KA-BLR-02", "TN-CHN-03"])

try:
    feedback_response = requests.get(f"{FEEDBACK_BASE_URL}/{target_office}", timeout=10)
    if feedback_response.status_code == 200:
        data = feedback_response.json()
        telemetry = data.get("aggregate_telemetry", {})
        comments_list = data.get("recent_sanitized_comments", [])
        
        # Display aggregate volume thresholds
        st.write(f"**Total Review Records Registered for Center:** {telemetry.get('total_reviews_count', 0)}")
        
        # Display the sanitized comment list feed securely
        st.markdown("#### Recent Sanitized Public Feedback Logs")
        if not comments_list:
            st.info("No anonymous review entries logged for this municipal office.")
        for item in comments_list:
            st.info(f"⭐ **Rating: {item['rating_given']}/5** — Description: \"{item['comment_body']}\"")
except Exception as e:
    st.warning(f"Could not load live experience review metrics at this time: {str(e)}")

