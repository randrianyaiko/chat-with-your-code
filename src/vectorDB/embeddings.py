from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

embeddings = FastEmbedEmbeddings(model_name=os.getenv("FASTEMBED_MODEL"),
                                 cache_dir=os.getenv("FASTEMBED_CACHE_DIR"),)
