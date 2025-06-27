import streamlit as st
import traceback
from core.file_handler import process_sources
from src.agent.agents import Agents
from src.vectorDB.vectordb import VectorStore
import os

def handle_submit(uploaded_files, repo_url):
    if not uploaded_files and not repo_url:
        st.sidebar.warning("⚠️ Please upload files or enter a repo URL.")
        return False
    if not st.session_state.gemini_api_key.strip():
        st.sidebar.warning("⚠️ API key required.")
        return False

    with st.spinner("🔍 Reading sources..."):
        try:
            filepaths = process_sources(
                uploaded_files, repo_url, st.session_state, st.sidebar
            )

            if not filepaths:
                st.sidebar.error("❌ No usable files found.")
                return False

            st.session_state.vectorstore = VectorStore(filepaths)
            st.session_state.agent = Agents(
                st.session_state.vectorstore,
                st.session_state.project_tree
            )

            st.sidebar.success("✅ Sources processed successfully.")
            return filepaths
        except Exception:
            st.sidebar.error("❌ Error during processing.")
            st.sidebar.code(traceback.format_exc(), language="python")
            return False

def preview_uploaded_files(filepaths):
    if not filepaths:
        return
    st.subheader("📂 File Previews")
    for path in filepaths:
        st.markdown(f"**{os.path.basename(path)}**")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                preview = "".join(f.readlines()[:15])
            st.code(preview)
        except Exception:
            st.code("⚠️ Cannot preview this file", language="text")
