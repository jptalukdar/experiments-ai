import streamlit as st
import requests
import json

# --- Configuration ---
FASTAPI_URL = "http://127.0.0.1:8000/api/v1/chat"
st.set_page_config(page_title="AI Agent Chat", layout="centered")
st.title("🤖 AI Agent Chat")
st.caption(f"A Streamlit frontend for the FastAPI AI agent running at `{FASTAPI_URL}`")

# --- Helper Function to Call API ---

def call_fastapi(prompt: str):
    """
    Sends a prompt to the FastAPI backend and gets a response.
    Returns (ai_response, debug_info)
    """
    payload = {"prompt": prompt}
    try:
        response = requests.post(FASTAPI_URL, json=payload, timeout=300)
        
        # Check for HTTP errors
        response.raise_for_status() 
        
        data = response.json()
        ai_response = data.get("response", "Error: No 'response' key in JSON.")
        debug_info = data.get("debug_info")
        return ai_response, debug_info

    except requests.exceptions.ConnectionError:
        st.error(f"**Connection Error:** Could not connect to the FastAPI backend at `{FASTAPI_URL}`. Please ensure the backend server is running.")
        return None, None
    except requests.exceptions.HTTPError as e:
        st.error(f"**HTTP Error:** {e.response.status_code} {e.response.reason}. Response: `{e.response.text}`")
        return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"**An unexpected error occurred:** {e}")
        return None, None

# --- Chat History Management ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "debug" in message and message["debug"]:
            with st.expander("Show Debug Info"):
                st.json(message["debug"])

# --- Chat Input and Response Logic ---

if prompt := st.chat_input("What's on your schedule?"):
    # 1. Add and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get (and display) the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            ai_response, debug_info = call_fastapi(prompt)

        if ai_response:
            st.markdown(ai_response)
            if debug_info:
                with st.expander("Show Debug Info"):
                    st.json(debug_info)
            
            # 3. Add assistant's response to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": ai_response,
                "debug": debug_info
            })
