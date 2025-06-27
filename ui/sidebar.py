import streamlit as st

def sidebar_api_key():
    st.write("Enter your Google Gemini API Key.")
    st.session_state.gemini_api_key = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        placeholder="Paste your Gemini API Key"
    )

def sidebar_upload_docs():
    return st.file_uploader(
        "📄 Upload files",
        type=["pdf", "docx", "txt", "csv", "json", "py"],
        accept_multiple_files=True
    )

def sidebar_git_repo_url():
    return st.text_input(
        "🔗 GitHub Repo URL",
        placeholder="https://github.com/user/repo"
    )

def sidebar_content_type():
    st.session_state.content_type = st.selectbox(
        "📝 Output Type",
        ["Documentation", "Technical Article", "Blog Post"],
        index=["Documentation", "Technical Article", "Blog Post"].index(st.session_state.content_type)
    )

def sidebar_controls():
    with st.sidebar:
        st.title("⚙️ Settings")
        sidebar_api_key()
        uploaded_files = sidebar_upload_docs()
        repo_url = sidebar_git_repo_url()
        sidebar_content_type()

        if st.button("♻️ Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        return uploaded_files, repo_url
