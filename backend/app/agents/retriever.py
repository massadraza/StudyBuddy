from typing import Dict, Any, List
from langchain_core.documents import Document

def retriever_agent(question: str, vectorstore) -> Dict[str, Any]:
    """Fetches examples/definitions from the vector database"""
    print(f"[Retriever Agent] Searching for: {question}")
    
    docs: List[Document] = vectorstore.similarity_search(question, k=3)
    
    # Simple topic extraction (will be refined by topic_extractor if needed)
    topic = question[:30].lower() if len(question) < 30 else question[:30].lower() + "..."
    
    return {
        "retrieved_docs": docs,
        "current_topic": topic
    }
