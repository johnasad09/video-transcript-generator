"""
main.py - Streamlit app that sends a URL to an n8n webhook and displays the response.

Flow:
  1. User enters a URL
  2. URL is validated (url_validator.py)
  3. Valid URL is POSTed to the n8n webhook trigger
  4. n8n processes it and responds via its "Respond to Webhook" node
  5. The response is displayed in the UI
"""

import requests
import streamlit as st
# from dotenv import load_dotenv
# import os

from url_validator import is_valid_url

# load_dotenv()

st.set_page_config(page_title="Transcript Generator", layout="centered")
st.title("Video Transcript Generator")

webhook_url = st.secrets["config"]["N8N_WEBHOOK_URL"]

# Initialize session state for persisting results
if "summary" not in st.session_state:
    st.session_state.summary = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None

url_input = st.text_input(
    "Video / Content URL",
    placeholder="Paste Video URL (YouTube, Insta, TikTok)",
)

submitted = st.button("Transcribe", type="primary")

if submitted:
    # Clear previous results when a new request is made
    st.session_state.summary = None
    st.session_state.transcript = None

    with st.spinner("Processing..."):
        # Validate the content URL
        valid, error = is_valid_url(url_input)
        if not valid:
            st.error(f"Invalid URL: {error}")
            st.stop()

        # Validate the webhook URL
        webhook_valid, webhook_error = is_valid_url(webhook_url)
        if not webhook_valid:
            st.error(f"Invalid webhook URL: {webhook_error}")
            st.stop()

        st.info(f"Fetching Data: `{url_input}`")

        payload = {"url": url_input}
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            st.error("Request timed out. Server did not respond within 120 seconds.")
            st.stop()
        except requests.exceptions.RequestException as exc:
            st.error(f"Failed to reach the Server: {exc}")
            st.stop()

    st.success("Response received from server.")

    # n8n responds with JSON containing both summary and transcript.
    try:
        data = response.json()
        st.session_state.summary = data.get("summary", "").strip()
        st.session_state.transcript = data.get("transcript", "").strip()
    except Exception:
        st.session_state.summary = response.text.strip()
        st.session_state.transcript = ""

# Display persisted results
if st.session_state.summary is not None:
    st.subheader("Result")
    if st.session_state.summary:
        st.markdown(st.session_state.summary)
    else:
        st.warning("Empty response returned.")

    if st.session_state.transcript:
        st.download_button(
            label="Download Transcript",
            data=st.session_state.transcript,
            file_name="transcript.txt",
            mime="text/plain",
            type="primary",
        )
