from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    PythonLoader,
    UnstructuredCSVLoader,
    TextLoader,
    JSONLoader,
)

def loadAndSplitDocuments(paths: List[str]) -> List[Document]:
    all_documents = []

    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    for path in paths:
        loaded_docs = []

        if path.endswith('.pdf'):
            loader = PyMuPDFLoader(path)
            loaded_docs = loader.load()

        elif path.endswith('.docx'):
            loader = Docx2txtLoader(path)
            loaded_docs = loader.load()

        elif path.endswith('.py'):
            loader = PythonLoader(path)
            loaded_docs = loader.load()

        elif path.endswith('.csv'):
            loader = UnstructuredCSVLoader(path)
            loaded_docs = loader.load()

        elif path.endswith(('.txt','.md','.yml','.yaml')):
            loader = TextLoader(path)
            loaded_docs = loader.load()

        elif path.endswith('.json'):
            loader = JSONLoader(
                file_path=path,
                jq_schema=".[]",  # Adjust as needed
                text_content=False
            )
            loaded_docs = loader.load()

        else:
            print(f"Unsupported file format: {path}")
            continue

        # Split each document into chunks
        split_docs = splitter.split_documents(loaded_docs)
        all_documents.extend(split_docs)

    return all_documents
