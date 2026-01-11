from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from ..config import settings

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=settings.openai_api_key,
    temperature=0.3
)

def topic_extractor_agent(question: str, retrieved_docs: List[Document]) -> Dict[str, Any]:
    """Extracts the main topic/concept from the question or retrieved docs"""
    context = retrieved_docs[0].page_content if retrieved_docs else ""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Extract the main topic or concept from this question and context.
         Return ONLY a short topic name (1-3 words, lowercase).
         Examples: "polymorphism", "inheritance", "variables", "functions"
         
         Context: {context}
         Question: {question}
         
         Topic (1-3 words only):"""),
        ("human", "Extract the topic.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"context": context[:200], "question": question})
    
    topic = response.content.strip().lower().replace('"', '').replace("'", "")
    
    # Fallback if topic is too long or empty
    if len(topic) > 30 or len(topic) == 0:
        topic = question[:30] if question else "general"
    
    print(f"[Topic Extractor] Identified topic: {topic}")
    
    return {"current_topic": topic}
