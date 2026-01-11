from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from ..config import settings

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=settings.openai_api_key,
    temperature=0.9
)

def question_generator_agent(retrieved_docs: List[Document]) -> Dict[str, Any]:
    """Generates practice questions from study material"""
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a question generator. Create practice questions from the study material.
         Format your response EXACTLY as:
         QUESTION: <your question here>
         ANSWER: <detailed correct answer here>
         
         Context: {context}"""),
        ("human", "Generate one practice question based on this material.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"context": context})
    
    # Parse question and answer
    lines = response.content.strip().split("\n")
    question = ""
    answer = ""
    
    for line in lines:
        if line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()
    
    print(f"[Question Generator] Generated: {question[:50]}...")
    
    return {
        "generated_question": question,
        "correct_answer": answer
    }
