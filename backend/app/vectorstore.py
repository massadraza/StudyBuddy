from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .config import settings
from pathlib import Path

# Directory where user study guides are stored
UPLOAD_DIR = Path("uploaded_study_guides")


class VectorStoreManager:
    """Manages per-user FAISS vector stores for study guides"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self._cache = {}  # Cache loaded vectorstores by user_id

    def get_user_vectorstore(self, user_id: int):
        """Load and return the vectorstore for a specific user"""
        # Check cache first
        if user_id in self._cache:
            return self._cache[user_id]

        # Build path to user's vectorstore
        vectorstore_path = UPLOAD_DIR / str(user_id) / "vectorstore"

        if not vectorstore_path.exists():
            raise ValueError(f"No study guide found for user {user_id}. Please upload a study guide first.")

        # Load the vectorstore
        vectorstore = FAISS.load_local(
            str(vectorstore_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        # Cache it
        self._cache[user_id] = vectorstore

        return vectorstore

    def clear_user_cache(self, user_id: int):
        """Clear cached vectorstore for a user (call after they upload a new study guide)"""
        if user_id in self._cache:
            del self._cache[user_id]

    def user_has_vectorstore(self, user_id: int) -> bool:
        """Check if a user has an uploaded study guide"""
        vectorstore_path = UPLOAD_DIR / str(user_id) / "vectorstore"
        return vectorstore_path.exists()

# Global instance
vector_manager = VectorStoreManager()