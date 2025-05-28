import streamlit as st
import tempfile
import os
import subprocess
from urllib.parse import urlparse
import traceback
from src.agent.agents import Agents
from src.vectorDB.vectordb import VectorStore


# -------------------- SESSION STATE -------------------- #
def init_session_state():
    defaults = {
        "messages": [],
        "vectorstore": None,
        "agent": None,
        "gemini_api_key": "",
        "project_tree": "",
        "content_type": "Documentation"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# -------------------- SIDEBAR UI -------------------- #
def sidebar_api_key():
    st.write(
        "Your Google Gemini API Key is required to enable the assistant.\n\n"
        "🔒 **Security:** Your API key is stored **only for this session**."
    )
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="Paste your Gemini API key here",
        value=st.session_state.gemini_api_key,
    )
    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key


def sidebar_upload_docs():
    st.write(
        "Upload files like PDF, DOCX, TXT, CSV, JSON, or Python. These documents will be used by the assistant."
    )
    return st.file_uploader(
        "Select one or more files",
        type=["pdf", "docx", "txt", "csv", "json", "py"],
        accept_multiple_files=True
    )


def sidebar_git_repo_url():
    st.write("Enter the URL of a public GitHub repository.")
    return st.text_input(
        "Git Repository URL",
        placeholder="https://github.com/user/repo"
    )


def sidebar_content_type():
    st.session_state.content_type = st.selectbox(
        "Select output type",
        ["Documentation", "Technical Article", "Blog Post"],
        index=["Documentation", "Technical Article", "Blog Post"].index(st.session_state.content_type)
    )


def sidebar_controls():
    with st.sidebar.expander("🔑 API Configuration", expanded=True):
        sidebar_api_key()

    with st.sidebar.expander("📄 Upload Documents"):
        uploaded_files = sidebar_upload_docs()

    with st.sidebar.expander("🧬 Git Repository"):
        repo_url = sidebar_git_repo_url()

    with st.sidebar.expander("📝 Output Format"):
        sidebar_content_type()

    if st.sidebar.button("♻️ Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    return uploaded_files, repo_url


# -------------------- FILE & REPO HANDLING -------------------- #
def get_repo_name_from_url(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    return os.path.splitext(os.path.basename(parsed.path))[0]


def get_directory_tree(root_dir: str) -> str:
    tree = []
    for root, dirs, files in os.walk(root_dir):
        level = root.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        tree.append(f"{indent}📁 {os.path.basename(root)}/")
        subindent = "    " * (level + 1)
        for f in files:
            tree.append(f"{subindent}📄 {f}")
    return "\n".join(tree)


def process_sources(uploaded_files, repo_url):
    filepaths = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.read())
                filepaths.append(tmp_file.name)

    if repo_url:
        repo_name = get_repo_name_from_url(repo_url)
        base_dir = tempfile.mkdtemp()
        clone_path = os.path.join(base_dir, repo_name)
        try:
            subprocess.run(["git", "clone", repo_url, clone_path], check=True)
            st.session_state.project_tree = get_directory_tree(clone_path)
            st.sidebar.subheader(f"🗂️ Project: `{repo_name}`")
            st.sidebar.code(st.session_state.project_tree, language="text")
            for root, _, files in os.walk(clone_path):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.csv', '.json')):
                        filepaths.append(os.path.join(root, file))
        except subprocess.CalledProcessError as e:
            st.sidebar.error(f"❌ Failed to clone repo: {e}")

    return filepaths


def preview_uploaded_files(filepaths):
    if not filepaths:
        return
    st.subheader("📂 Uploaded File Previews")
    for path in filepaths:
        st.markdown(f"**{os.path.basename(path)}**")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                preview = "".join(f.readlines()[:15])
            st.code(preview, language="python")
        except Exception:
            st.code("Unable to preview this file.", language="text")


# -------------------- CORE LOGIC -------------------- #
def handle_submit(all_inputs):
    if not all_inputs:
        st.sidebar.warning("⚠️ Please upload files or enter a GitHub repo URL.")
        return False
    if not st.session_state.gemini_api_key.strip():
        st.sidebar.warning("⚠️ Please enter your Google Gemini API Key.")
        return False

    with st.spinner("🔄 Processing sources..."):
        try:
            st.session_state.vectorstore = VectorStore(all_inputs)
            st.session_state.agent = Agents(
                st.session_state.vectorstore,
                st.session_state.project_tree
            )
            st.sidebar.success("✅ Sources added successfully.")
            return True
        except Exception as e:
            st.sidebar.error("❌ Failed to process sources.")
            st.sidebar.code(traceback.format_exc(), language="python")
            return False


# -------------------- CHAT UI -------------------- #
def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat_interface():
    if not (st.session_state.vectorstore and st.session_state.gemini_api_key.strip()):
        st.info(
            "ℹ️ Please enter your API key and upload files or provide a repo URL to start chatting.",
            icon="💡"
        )
        return

    if prompt := st.chat_input("Ask me anything about your code or documents..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("✍️ Thinking..."):
            response = st.session_state.agent.run(prompt, content_type=st.session_state.content_type)

        with st.chat_message("assistant"):
            with st.expander("📄 Generated Content", expanded=True):
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


# -------------------- MAIN -------------------- #
def main():
    st.set_page_config(page_title="Chat with your code", layout="wide")
    st.title("💻 Chat with your code")
    st.caption("AI assistant for generating documentation, articles, and blogs from your codebase.")

    init_session_state()

    uploaded_files, repo_url = sidebar_controls()

    if st.sidebar.button("📥 Submit Sources", disabled=not st.session_state.gemini_api_key.strip()):
        all_inputs = process_sources(uploaded_files, repo_url)
        success = handle_submit(all_inputs)
        if success:
            preview_uploaded_files(all_inputs)

    st.divider()
    st.subheader("💬 Chat with Your Assistant")
    display_chat_history()
    chat_interface()


if __name__ == "__main__":
    main()
