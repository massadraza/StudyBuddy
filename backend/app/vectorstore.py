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
        self.connection_string = settings.vector_connection

    def _get_embeddings(self, openai_api_key: str) -> OpenAIEmbeddings:
        """Get embeddings instance with the provided API key"""
        return OpenAIEmbeddings(openai_api_key=openai_api_key)

    def _get_base_vectorstore(self, openai_api_key: str) -> PGVector:
        """Get the base PGVector store connection"""
        return PGVector(
            embeddings=self._get_embeddings(openai_api_key),
            connection=self.connection_string,
            collection_name=COLLECTION_NAME,
            use_jsonb=True,
        )

    def get_user_vectorstore(self, user_id: int, openai_api_key: str) -> UserFilteredVectorStore:
        """
        Return a vectorstore configured to filter by user_id.
        """
        # Check if user has documents
        if not self.user_has_vectorstore(user_id, openai_api_key):
            raise ValueError(
                f"No study guide found for user {user_id}. "
                "Please upload a study guide first."
            )

        # Create a wrapper that applies user_id filter
        vectorstore = self._get_base_vectorstore(openai_api_key)
        user_vectorstore = UserFilteredVectorStore(vectorstore, user_id)

        return user_vectorstore

    def add_documents_for_user(
        self,
        user_id: int,
        texts: List[str],
        openai_api_key: str,
        metadatas: Optional[List[dict]] = None
    ) -> List[str]:
        """Add documents for a specific user"""
        vectorstore = self._get_base_vectorstore(openai_api_key)

        # Ensure user_id is in all metadata
        if metadatas is None:
            metadatas = [{"user_id": user_id} for _ in texts]
        else:
            for m in metadatas:
                m["user_id"] = user_id

        # Add texts and return document IDs
        ids = vectorstore.add_texts(texts=texts, metadatas=metadatas)

        return ids

    def delete_user_documents(self, user_id: int, openai_api_key: str) -> None:
        """Delete all documents for a specific user"""
        vectorstore = self._get_base_vectorstore(openai_api_key)

        # Delete documents matching user_id filter
        vectorstore.delete(filter={"user_id": user_id})

    def user_has_vectorstore(self, user_id: int, openai_api_key: str) -> bool:
        """Check if a user has documents in the vectorstore"""
        vectorstore = self._get_base_vectorstore(openai_api_key)

        # Perform a search with filter to check if any docs exist
        results = vectorstore.similarity_search(
            query="test",
            k=1,
            filter={"user_id": user_id}
        )

        return len(results) > 0


# Global instance
vector_manager = VectorStoreManager()
