"""
LangGraph-based multi-agent tutor workflow.

This module defines a single StateGraph that routes between agents based on mode:
- "qa": Retriever -> Tutor -> END
- "practice": Retriever -> Question Generator -> END
- "evaluate": Retriever -> Evaluator -> Topic Extractor -> Mastery Tracker -> END
"""

from typing import TypedDict, List, Annotated, Any, Optional
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from .config import settings
from .models.database_models import MasteryScore


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=settings.openai_api_key,
    temperature=0
)

llm_creative = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=settings.openai_api_key,
    temperature=0.7
)


class TutorState(TypedDict):
    """Shared state for the tutor graph."""
    # Input fields
    mode: str  # "qa" | "practice" | "evaluate"
    question: str
    student_answer: Optional[str]

    # Database context (passed in, not modified by graph)
    user_id: int
    vectorstore: Any  # FAISS vectorstore
    db: Session

    # Intermediate state
    retrieved_docs: List[Document]
    current_topic: str
    generated_question: str
    correct_answer: str

    # Output fields
    answer: str
    is_correct: bool
    feedback: str
    new_mastery_score: float
    chat_history: Annotated[List[BaseMessage], operator.add]


# ============ Agent Node Functions ============

def retriever_node(state: TutorState) -> dict:
    """Fetches relevant documents from the vector database."""
    question = state["question"]
    vectorstore = state["vectorstore"]

    print(f"[Retriever] Searching for: {question[:50]}...")
    docs = vectorstore.similarity_search(question, k=3)

    # Simple topic extraction (refined by topic_extractor if needed)
    topic = question[:30].lower() if len(question) < 30 else question[:30].lower() + "..."

    return {
        "retrieved_docs": docs,
        "current_topic": topic
    }


def tutor_node(state: TutorState) -> dict:
    """Provides explanations with examples and analogies."""
    question = state["question"]
    docs = state["retrieved_docs"]

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a patient tutor. Explain concepts clearly with analogies and examples.
Use the context from the study guide to provide accurate information.

Context from study guide:
{context}"""),
        ("human", "{question}")
    ])

    chain = prompt | llm_creative
    response = chain.invoke({"context": context, "question": question})

    print(f"[Tutor] Generated response")

    return {
        "answer": response.content,
        "chat_history": [
            HumanMessage(content=question),
            AIMessage(content=response.content)
        ]
    }


def question_generator_node(state: TutorState) -> dict:
    """Generates practice questions from the study material."""
    docs = state["retrieved_docs"]
    topic = state.get("current_topic", "this topic")

    print(f"[Question Generator] Creating practice question about {topic}...")

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a question generator. Based on the context, create ONE practice question.

Context:
{context}

Generate a question that tests understanding. Format your response EXACTLY like this:

QUESTION: [your question here]
ANSWER: [the correct answer]"""),
        ("human", "Generate a practice question.")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context})

    # Parse response
    lines = response.content.split("\n")
    question = ""
    answer = ""

    for line in lines:
        if line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()

    return {
        "generated_question": question,
        "correct_answer": answer
    }


def evaluator_node(state: TutorState) -> dict:
    """Evaluates student answers against correct answers."""
    student_answer = state["student_answer"]
    correct_answer = state["correct_answer"]
    question = state["generated_question"]

    print("[Evaluator] Checking answer...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an evaluator. Compare the student's answer to the correct answer.

Question: {question}
Correct Answer: {correct_answer}
Student Answer: {student_answer}

Determine if the student is correct (consider synonyms and paraphrasing).
Provide helpful feedback.

Format your response:
CORRECT: yes or no
FEEDBACK: [your detailed feedback]"""),
        ("human", "Evaluate the answer.")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "question": question,
        "correct_answer": correct_answer,
        "student_answer": student_answer
    })

    is_correct = "correct: yes" in response.content.lower()

    # Parse feedback
    feedback_lines = response.content.split("\n")
    feedback = ""
    for line in feedback_lines:
        if line.upper().startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip() if ":" in line else ""

    if not feedback:
        feedback = response.content

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "answer": feedback  # For compatibility
    }


def topic_extractor_node(state: TutorState) -> dict:
    """Extracts the main topic from the question and context."""
    question = state.get("question", "") or state.get("generated_question", "")
    docs = state.get("retrieved_docs", [])

    context = docs[0].page_content if docs else ""

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

    # Clean up response
    topic = response.content.strip().lower().replace('"', '').replace("'", "")

    # Fallback if response is too long or empty
    if len(topic) > 30 or len(topic) == 0:
        topic = question[:30] if question else "general"

    print(f"[Topic Extractor] Identified topic: {topic}")

    return {"current_topic": topic}


def mastery_tracker_node(state: TutorState) -> dict:
    """Updates mastery scores in the database."""
    topic = state.get("current_topic", "general")
    is_correct = state.get("is_correct", False)
    user_id = state["user_id"]
    db = state["db"]

    # Get or create mastery score
    mastery_score = db.query(MasteryScore).filter(
        MasteryScore.user_id == user_id,
        MasteryScore.topic == topic
    ).first()

    if not mastery_score:
        mastery_score = MasteryScore(
            user_id=user_id,
            topic=topic,
            score=0.5
        )
        db.add(mastery_score)

    current_score = mastery_score.score

    # Update score
    if is_correct:
        new_score = min(1.0, current_score + 0.1)
        print(f"[Mastery Tracker] {topic}: {current_score:.0%} -> {new_score:.0%}")
    else:
        new_score = max(0.0, current_score - 0.15)
        print(f"[Mastery Tracker] {topic}: {current_score:.0%} -> {new_score:.0%}")

    mastery_score.score = new_score
    db.commit()
    db.refresh(mastery_score)

    return {"new_mastery_score": new_score}


# ============ Routing Function ============

def route_by_mode(state: TutorState) -> str:
    """Routes to different agents based on mode."""
    mode = state.get("mode", "qa")

    if mode == "practice":
        print("[Router] Practice mode -> Question Generator")
        return "question_generator"
    elif mode == "evaluate":
        print("[Router] Evaluate mode -> Evaluator")
        return "evaluator"
    else:
        print("[Router] Q&A mode -> Tutor")
        return "tutor"


# ============ Build the Graph ============

def build_tutor_graph() -> StateGraph:
    """Builds and compiles the tutor workflow graph."""

    workflow = StateGraph(TutorState)

    # Add nodes
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("question_generator", question_generator_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("topic_extractor", topic_extractor_node)
    workflow.add_node("mastery_tracker", mastery_tracker_node)

    # Set entry point
    workflow.set_entry_point("retriever")

    # Add conditional routing after retriever
    workflow.add_conditional_edges(
        "retriever",
        route_by_mode,
        {
            "tutor": "tutor",
            "question_generator": "question_generator",
            "evaluator": "evaluator"
        }
    )

    # Add edges to END
    workflow.add_edge("tutor", END)
    workflow.add_edge("question_generator", END)

    # Evaluate flow: evaluator -> topic_extractor -> mastery_tracker -> END
    workflow.add_edge("evaluator", "topic_extractor")
    workflow.add_edge("topic_extractor", "mastery_tracker")
    workflow.add_edge("mastery_tracker", END)

    return workflow.compile()


# Compile the graph
tutor_graph = build_tutor_graph()
print("LangGraph tutor workflow compiled successfully!")
