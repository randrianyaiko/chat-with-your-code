import streamlit as st

def init_session_state():
    defaults = {
        "messages": [],
        "vectorstore": None,
        "agent": None,
        "gemini_api_key": "",
        "project_tree": "",
        "content_type": "Documentation",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
