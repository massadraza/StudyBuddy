import os, json
from typing import TypedDict, List, Annotated, Dict, Optional
import operator
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# Define the State of the Graph
class TutorState(TypedDict):
    question: str
    chat_history: Annotated[List[BaseMessage], operator.add]
    retrieved_docs: List
    answer: str
    user_feedback: str 
    mode: str # "qa" | "practice" | "evaluate"
    generated_question: str
    correct_answer: str
    student_answer: str
    is_correct: bool
    current_topic: str
    mastery_scores: Dict[str, float]


# Load the study guide and create the vector store
with open("study_guide.txt", "r", encoding="utf-8") as f:
    text = f.read()

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text(text)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

print("Study guide loaded and vectoried!")

# Retriever Agent
def retriever_agent(state: TutorState):
    """Fetches examples / definitions from the vector database"""
    question = state["question"]
    print(f"[Retriever Agent] Searching for {question}")
    docs = vectorstore.similarity_search(question, k=3)
    return {"retrieved_docs": docs}

# Tutor Agent
def tutor_agent(state: TutorState):
    """Provides examples and analogies"""
    question = state["question"]
    docs = state["retrieved_docs"]
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a patient tutor. Explain concepts clearly with analogies.
         Context from study guide: {context}"""), ("human", "{question}")
    ])

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    return {
        "answer": response.content,
        "chat_history":[
            HumanMessage(content=question),
            AIMessage(content=response.content)
        ]
    }

def question_generator_agent(state: TutorState):
    """Creates adaptive practice questions"""
    docs = state["retrieved_docs"]
    topic = state.get("current_topic", "this topic")

    print(f" [Question Generator Agent] Creating practice question about {topic}...")
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
    lines = response.content.split("\n")
    question = ""
    answer  = ""

    for line in lines:
        if line.startswith("QUESTION:"):
            question = line.replace("QUESTION:", "").strip()
        elif line.startswith("ANSWER:"):
            answer = line.replace("ANSWER:", "").strip()

    return{
        "generated_question": question,
        "correct_answer": answer
    }   

def evaluator_agent(state: TutorState):
    """Grades answers, detects misconceptions, updates mastery"""
    student_answer = state["student_answer"]
    correct_answer = state["correct_answer"]
    question = state["generated_question"]

    print("[Evaluator Agent] Checking your answer...")

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
    response = chain.invoke({"question": question, "correct_answer": correct_answer, "student_answer": student_answer})
    is_correct = "CORRECT: yes" in response.content.lower()

    feedback_lines = response.content.split("\n")
    feedback = ""
    for line in feedback_lines:
        if line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()
        
    if not feedback:
        feedback = response.content

    return {
        "is_correct": is_correct,
        "answer": feedback
    }

def decide_node(state: TutorState):
    """Routes to different agents based on mode"""
    mode = state.get("mode", "qa")

    if mode == "practice":
        print("[Router] Practice mode -> Question Generator")
        return "generate"
    elif mode == "evaluate":
        print("[Router] Evaluate mode -> Evaluator")
        return "evaluate"
    else:
        print("[Router] Q&A mode -> Tutor")
        return "tutor"
    

workflow = StateGraph(TutorState)
workflow.add_node("retriever", retriever_agent)
workflow.add_node("tutor", tutor_agent)
workflow.add_node("question_generator", question_generator_agent)
workflow.add_node("evaluator", evaluator_agent)

workflow.set_entry_point("retriever")

workflow.add_conditional_edges(
    "retriever",
    decide_node,
    {
        "tutor": "tutor",
        "generate": "question_generator",
        "evaluate": "evaluator"
    }
)

workflow.add_edge("tutor", END)
workflow.add_edge("question_generator", END)
workflow.add_edge("evaluator", END)

app = workflow.compile()
print("Multi-agent graph was built successfully!")

# Main Loop Execution
print("\n Welcome to your Multi-Agent AI Tutor!")
print("Commands:")
print(" - Ask any question for the Q&A mode")
print(" - Type 'practice' to get a practice question")
print(" - Type 'exit' to quit \n")

chat_history = []

while True:
    query = input("You: ")

    if query.lower() in ["exit", "quit"]:
        print("Goodbye! Happy Studying!")
        break

    if query.lower() == "practice":
        result = app.invoke({
            "mode": "practice",
            "question": "Generate a practice question from study guide",
            "chat_history": chat_history,
            "retrieved_docs": []
        })

        print(f"Practice Question: {result['generated_question']}\n")

        student_answer = input("Your answer: ")

        if student_answer.lower() in ["skip", ""]:
            print(f"\n The answer was: {result['correct_answer']}\n")
            continue

        eval_result = app.invoke({
            "mode": "evaluate",
            "question": result['generated_question'],
            "generated_question": result['generated_question'],
            "correct_answer": result["correct_answer"],
            "student_answer": student_answer,
            "retrieved_docs": result["retrieved_docs"]

        })

        if eval_result["is_correct"]:
            print(f"\n✅ Correct! {eval_result['answer']}\n")
        else:
            print(f"\n❌ Not quite. {eval_result['answer']}\n")
            print(f"💡 The correct answer was: {result['correct_answer']}\n")
        
    else:
        result = app.invoke({
            "mode": "qa",
            "question": query,
            "chat_history": chat_history,
            "retrieved_docs": []
        }
        )

        print(f"\n Tutor: {result['answer']}")

        chat_history = result.get("chat_history", chat_history)