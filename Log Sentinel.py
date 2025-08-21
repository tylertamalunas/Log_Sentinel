import streamlit as st
import google.generativeai as genai
import json

# --- Project Name and Description ---
PROJECT_NAME = "Log Sentinel"
PROJECT_DESCRIPTION = """
This log analyzer uses the Gemini API to act as a security analyst, triaging logs and
identifying potential threats. It processes both text and JSON-formatted logs.
"""

# --- Gemini API Configuration ---
# Set the API key from Streamlit secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("Gemini API key not found. Please add your key to the secrets.toml file.")
    st.stop()

# --- Main Application Logic ---
st.set_page_config(layout="wide", page_title=PROJECT_NAME)

st.title(PROJECT_NAME)
st.markdown(PROJECT_DESCRIPTION)
st.markdown("---")

st.subheader("Analyze your security log data")

# File uploader for log files
uploaded_file = st.file_uploader("Or, upload a log file (e.g., .txt, .log, .json)", type=["txt", "log", "json"])

# Text area for manual input
log_input = st.text_area(
    label="Paste log entries here:",
    height=300,
    placeholder="Paste your log data here, with each log entry on a new line."
)

if st.button("Analyze Logs", use_container_width=True):
    log_data = ""
    if uploaded_file is not None:
        log_data = uploaded_file.getvalue().decode("utf-8")
    elif log_input:
        log_data = log_input
    else:
        st.warning("Please paste some log entries or upload a file to analyze.")
        st.stop()

    # Create the prompt with a clear persona and instructions
    prompt = f"""
    You are an expert cybersecurity analyst.. Your primary role is to act as a log triage system. You will analyze the provided security log entries to identify potential threats and security risks. Your goal is to help a human analyst quickly prioritize which logs need immediate attention.

    Here are the rules for your analysis:
    - **CRITICAL**: An immediate, high-priority threat that requires urgent action. Look for signs of privilege escalation, data exposure (e.g., public S3 buckets), or activity from known malicious sources. Examples include 'PutBucketAcl', 'UpdateTrail', 'AttachUserPolicy', 'failed password for root'.
    - **SUSPICIOUS**: An unusual or noteworthy event that should be reviewed. Look for patterns like multiple failed logins for non-root users, unauthorized user attempts, or activity in an unusual region.
    - **INFO**: A routine, benign, and normal log entry. You must not report any log that you classify as INFO.

    The logs you are analyzing are a mix of standard Linux syslog, AWS S3 logs, and structured AWS CloudTrail JSON. You must be able to parse and understand all formats.

    For each log you identify as CRITICAL or SUSPICIOUS, you will format the output as a Markdown table with three columns: "Log Entry", "Severity", and "Explanation". If you find no potential issues, state that clearly.

    Logs to analyze:
    ---
    {log_data}
    ---
    """
    
    # Call the Gemini API for analysis
    with st.spinner("Analyzing logs with Gemini..."):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
            response = model.generate_content(prompt)
            st.markdown("---")
            st.subheader("Analysis Results")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")


