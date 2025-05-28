from langchain_community.vectorstores import FAISS
from src.vectorDB.documentLoader import loadAndSplitDocuments
from src.vectorDB.embeddings import embeddings
from typing import List, Dict, Set

class VectorStore:
    def __init__(self, filepaths: List[str]):
        self.library = None
        self.from_path(filepaths)  # Initialize vector store from documents
    
    def from_path(self, filepaths: List[str]):
        documents = loadAndSplitDocuments(filepaths)
        self.library = FAISS.from_documents(documents, embeddings)
    def search(self, query) -> List[Dict[str, str]]:
        
        print("Using the searching function")
        if self.library is None:
            raise ValueError("Vector store not initialized. Call from_path() first.")
        
        combined_results = []
        seen_texts: Set[str] = set()  # to avoid duplicate entries if desired
        
        print(f"Searching: {query}")
        results = self.library.similarity_search(query, k=10)
        results_ = []
        for doc in results:
            text = doc.page_content
            source = doc.metadata.get('source', 'unknown')
            results_.append({
                'text': text,
                'source': source
            })
        
        print(f"Found results: {results_}")
        return results_
    