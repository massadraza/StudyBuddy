from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from typing import List, Optional
from .config import settings

# Collection name for all study guide embeddings
COLLECTION_NAME = "study_guides"


class UserFilteredVectorStore:
    """
    Wrapper that applies user_id filtering to all similarity searches.
    Maintains compatibility with the existing API that expects
    vectorstore.similarity_search(query, k=3)
    """

    def __init__(self, vectorstore: PGVector, user_id: int):
        self._vectorstore = vectorstore
        self._user_id = user_id

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Search with automatic user_id filtering"""
        return self._vectorstore.similarity_search(
            query=query,
            k=k,
            filter={"user_id": self._user_id}
        )

    def similarity_search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """Search with scores and automatic user_id filtering"""
        return self._vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter={"user_id": self._user_id}
        )


class VectorStoreManager:
    """Manages per-user vector stores in PostgreSQL with pgvector"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.connection_string = settings.vector_connection
        self._cache = {}  # Cache vectorstore instances by user_id

    def _get_base_vectorstore(self) -> PGVector:
        """Get the base PGVector store connection"""
        return PGVector(
            embeddings=self.embeddings,
            connection=self.connection_string,
            collection_name=COLLECTION_NAME,
            use_jsonb=True,
        )

    def get_user_vectorstore(self, user_id: int) -> UserFilteredVectorStore:
        """
        Return a vectorstore configured to filter by user_id.
        """
        if user_id in self._cache:
            return self._cache[user_id]

        # Check if user has documents
        if not self.user_has_vectorstore(user_id):
            raise ValueError(
                f"No study guide found for user {user_id}. "
                "Please upload a study guide first."
            )

        # Create a wrapper that applies user_id filter
        vectorstore = self._get_base_vectorstore()
        user_vectorstore = UserFilteredVectorStore(vectorstore, user_id)

        self._cache[user_id] = user_vectorstore
        return user_vectorstore

    def add_documents_for_user(
        self,
        user_id: int,
        texts: List[str],
        metadatas: Optional[List[dict]] = None
    ) -> List[str]:
        """Add documents for a specific user"""
        vectorstore = self._get_base_vectorstore()

        # Ensure user_id is in all metadata
        if metadatas is None:
            metadatas = [{"user_id": user_id} for _ in texts]
        else:
            for m in metadatas:
                m["user_id"] = user_id

        # Add texts and return document IDs
        ids = vectorstore.add_texts(texts=texts, metadatas=metadatas)

        # Clear cache for this user
        self.clear_user_cache(user_id)

        return ids

    def delete_user_documents(self, user_id: int) -> None:
        """Delete all documents for a specific user"""
        vectorstore = self._get_base_vectorstore()

        # Delete documents matching user_id filter
        vectorstore.delete(filter={"user_id": user_id})

        self.clear_user_cache(user_id)

    def clear_user_cache(self, user_id: int):
        """Clear cached vectorstore for a user"""
        if user_id in self._cache:
            del self._cache[user_id]

    def user_has_vectorstore(self, user_id: int) -> bool:
        """Check if a user has documents in the vectorstore"""
        vectorstore = self._get_base_vectorstore()

        # Perform a search with filter to check if any docs exist
        results = vectorstore.similarity_search(
            query="test",
            k=1,
            filter={"user_id": user_id}
        )

        return len(results) > 0


# Global instance
vector_manager = VectorStoreManager()
