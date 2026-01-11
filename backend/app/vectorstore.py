from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from .config import settings
import os

class VectorStoreManager:
    """Manages FAISS vector store for study guides"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
    
    def load_study_guide(self, file_path: str = "study_guides/default_study_guide.txt"):
        """Load and vectorize a study guide"""
        full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)
        
        self.vectorstore = FAISS.from_texts(chunks, self.embeddings)
        print(f"Study guide loaded and vectorized from {file_path}")
        return self.vectorstore
    
    def get_vectorstore(self):
        """Get the current vectorstore"""
        if self.vectorstore is None:
            self.load_study_guide()
        return self.vectorstore

# Global instance
vector_manager = VectorStoreManager()
