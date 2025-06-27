import os
import tempfile
import subprocess
from urllib.parse import urlparse

def get_repo_name_from_url(url):
    parsed = urlparse(url)
    return os.path.splitext(os.path.basename(parsed.path))[0]

def get_directory_tree(path):
    tree = []
    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = "    " * level
        tree.append(f"{indent}📁 {os.path.basename(root)}/")
        subindent = "    " * (level + 1)
        for f in files:
            tree.append(f"{subindent}📄 {f}")
    return "\n".join(tree)

def process_sources(uploaded_files, repo_url, st_session_state, st_sidebar):
    filepaths = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                filepaths.append(tmp.name)

    if repo_url:
        repo_name = get_repo_name_from_url(repo_url)
        base_dir = tempfile.mkdtemp()
        clone_path = os.path.join(base_dir, repo_name)

        try:
            subprocess.run(["git", "clone", repo_url, clone_path], check=True)
            st_session_state.project_tree = get_directory_tree(clone_path)
            st_sidebar.subheader(f"🗂️ Project: `{repo_name}`")
            st_sidebar.code(st_session_state.project_tree, language="text")

            for root, _, files in os.walk(clone_path):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.csv', '.json')):
                        filepaths.append(os.path.join(root, file))

        except subprocess.CalledProcessError as e:
            st_sidebar.error(f"❌ Git clone failed: {e}")

    return filepaths
