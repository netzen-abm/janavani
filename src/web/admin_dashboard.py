import os

import pandas as pd
import requests
import streamlit as st

# Internal dashboard requires an explicitly configured interface credential.
API_GATEWAY_URL = os.getenv("JANAVANI_INTERNAL_API_URL", "http://ai-agent-service:8000/api/v1/agent/metrics")
FEEDBACK_BASE_URL = os.getenv("JANAVANI_INTERNAL_FEEDBACK_URL", "http://ai-agent-service:8000/api/v1/feedback/summary")
INTERFACE_TOKEN = os.getenv("ADMIN_INTERFACE_SECRET_TOKEN")

st.set_page_config(
    page_title="JanaVani — Internal Core Admin Console",
    page_icon="🇮🇳",
    layout="wide",
)

st.title("🇮🇳 JanaVani System Analytics Portal")
st.subheader("Privacy-by-Default Infrastructure Monitoring Terminal")

if not INTERFACE_TOKEN:
    st.error("Admin interface is not configured: ADMIN_INTERFACE_SECRET_TOKEN is required.")
    st.stop()

headers = {"X-Janavani-Interface-Token": INTERFACE_TOKEN}

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
    else:
        st.error(f"Failed to pull active metric grids. Gateway Status Code: {response.status_code}")
except requests.RequestException as error_trace:
    st.error(f"Metrics collection cluster currently unreachable: {error_trace}")

# --- Block 2: Municipal Office Performance Dashboard ---
st.markdown("---")
st.markdown("### 🏛️ Municipal Office Citizen Satisfaction Tracking Board")

target_office = st.selectbox(
    "Select Target Center to Inspect Accountabilities:",
    ["KL-TVM-01", "KA-BLR-02", "TN-CHN-03"],
)

try:
    feedback_response = requests.get(
        f"{FEEDBACK_BASE_URL}/{target_office}",
        headers=headers,
        timeout=10,
    )
    if feedback_response.status_code == 200:
        data = feedback_response.json()
        telemetry = data.get("aggregate_telemetry", {})
        comments_list = data.get("recent_sanitized_comments", [])

        st.write(
            f"**Total Review Records Registered for Center:** "
            f"{telemetry.get('total_reviews_count', 0)}"
        )

        st.markdown("#### Recent Sanitized Public Feedback Logs")
        if not comments_list:
            st.info("No anonymous review entries logged for this municipal office.")
        for item in comments_list:
            st.info(
                f"⭐ **Rating: {item.get('rating_given', '—')}/5** — "
                f"Description: \"{item.get('comment_body', '')}\""
            )
    else:
        st.warning(f"Feedback service returned status code: {feedback_response.status_code}")
except requests.RequestException as error_trace:
    st.warning(f"Could not load live experience review metrics at this time: {error_trace}")
