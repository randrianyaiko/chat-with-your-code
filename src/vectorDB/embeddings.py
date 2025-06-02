from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()


google_embeddings = GoogleGenerativeAIEmbeddings(model=os.getenv("GOOGLE_EMBEDDING_MODEL"),
                                          google_api_key=os.getenv('GOOGLE_API_KEY'))

fastembedding= FastEmbedEmbeddings(model_name=os.getenv("FAST_EMBEDDING_MODEL"))

models = {
    "google": google_embeddings,
    "fastembed": fastembedding
}

def get_embedding_model(model_name: str):
    """
    Returns the embedding model based on the provided model name.
    
    Args:
        model_name (str): The name of the embedding model to retrieve.
        
    Returns:
        Embedding model instance if found, otherwise raises ValueError.
    """
    if model_name in models:
        return models[model_name]
    else:
        raise ValueError(f"Embedding model '{model_name}' not found.")

embeddings = get_embedding_model(os.getenv("EMBEDDING_MODEL"))
