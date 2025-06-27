from langchain_community.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from src.vectorDB.documentLoader import loadAndSplitDocuments
from src.vectorDB.embeddings import embeddings
from typing import List, Dict, Set

class VectorStore:
    def __init__(self, filepaths: List[str]):
        self.library = None
        self.from_path(filepaths)  # Initialize vector store from documents
        self.results_template = """ You searched for "{query}" and here are the results:\n\n{results}"""
    def from_path(self, filepaths: List[str]):
        documents = loadAndSplitDocuments(filepaths)
        self.vector_library = FAISS.from_documents(documents, embeddings)
        self.bm25_retriever = BM25Retriever.from_documents(documents)
        self.vector_retriever = self.vector_library.as_retriever()
        self.library = EnsembleRetriever(retrievers=[self.vector_retriever, self.bm25_retriever])

    def formatResults(self, query:str, results: List[Dict]) -> str:
        search_results = ""
        for result in results:
            search_results += f"File: {result['source']}\n"
            search_results += f"Content: {result['text']}\n\n"
        return self.results_template.format(query=query, results=search_results)
    
    def search(self, query) -> List[Dict[str, str]]:    
        print("Using the searching function")
        if self.library is None:
            raise ValueError("Vector store not initialized. Call from_path() first.")
        
        combined_results = []
        seen_texts: Set[str] = set()  # to avoid duplicate entries if desired
        
        print(f"Searching: {query}")
        results = self.library.get_relevant_documents(query, k=7)
        results_ = []
        for doc in results:
            text = doc.page_content
            source = doc.metadata.get('source', 'unknown')
            results_.append({
                'text': text,
                'source': source
            })
        
        return results_
    
    def searchAndFormat(self, query: str) -> str:
        results = self.search(query)
        results = self.formatResults(query, results)
        print(f"Formatted results: {results}")
        return results
