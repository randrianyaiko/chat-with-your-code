import streamlit as st
from core.session import init_session_state
from ui.sidebar import sidebar_controls
from core.processing import handle_submit, preview_uploaded_files
from ui.chat import display_chat_history, chat_interface

def main():
    st.set_page_config("Chat with your Code", layout="wide")
    st.title("💬 Chat with Your Python Code")
    st.caption("Generate documentation, articles, and insights using AI from your codebase.")

    init_session_state()
    uploaded_files, repo_url = sidebar_controls()

    if st.sidebar.button("📥 Submit Sources"):
        filepaths = handle_submit(uploaded_files, repo_url)
        if filepaths:
            preview_uploaded_files(filepaths)

    st.divider()
    st.subheader("💡 Assistant")
    display_chat_history()
    chat_interface()

if __name__ == "__main__":
    main()
