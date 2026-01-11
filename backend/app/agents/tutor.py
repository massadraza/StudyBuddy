from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from ..config import settings

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=settings.openai_api_key,
    temperature=0.7
)

def tutor_agent(question: str, retrieved_docs: List[Document], chat_history: List) -> Dict[str, Any]:
    """Provides examples and analogies"""
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a patient tutor. Explain concepts clearly with analogies.
         Context from study guide: {context}"""),
        ("human", "{question}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    
    return {
        "answer": response.content,
        "chat_history": [
            HumanMessage(content=question),
            AIMessage(content=response.content)
        ]
    }
