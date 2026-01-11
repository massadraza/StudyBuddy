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

def evaluator_agent(
    generated_question: str,
    correct_answer: str,
    student_answer: str,
    retrieved_docs: List[Document]
) -> Dict[str, Any]:
    """Evaluates student answers"""
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an evaluator. Compare the student's answer to the correct answer.
         Be lenient with paraphrasing but check for accuracy.
         
         Question: {question}
         Correct Answer: {correct_answer}
         Student Answer: {student_answer}
         Context: {context}
         
         First, respond with ONLY "CORRECT" or "INCORRECT" on the first line.
         Then provide constructive feedback."""),
        ("human", "Evaluate this answer.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "question": generated_question,
        "correct_answer": correct_answer,
        "student_answer": student_answer,
        "context": context
    })
    
    # Parse response
    lines = response.content.strip().split("\n")
    is_correct = lines[0].strip().upper() == "CORRECT"
    feedback = "\n".join(lines[1:]).strip()
    
    print(f"[Evaluator] {'✅ Correct' if is_correct else '❌ Incorrect'}")
    
    return {
        "is_correct": is_correct,
        "user_feedback": feedback
    }
