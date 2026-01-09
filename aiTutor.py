from typing import TypedDict, List, Annotated
import operator
import os
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

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

with open("study_guide.txt", "r", encoding="utf-8") as f:
    text = f.read()

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text(text)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# Define State
class TutorState(TypedDict):
    question: str
    chat_history: Annotated[List[BaseMessage], operator.add]
    retrieved_docs: List
    answer: str
    user_feedback: str

# Retriever Node
def retriever_node(state: TutorState):
    """Searches vector database for relevant chunks"""
    question = state["question"]
    print(f"[Retriever Node] Searching for {question}")
    docs = vectorstore.similarity_search(question, k=3)
    return {"retrieved_docs": docs}

# LLM Node
def llm_node(state: TutorState):
    """Generate full answer"""
    question = state["question"]
    docs = state["retrieved_docs"]
    print("[LLM Node] Generating Full Answer...")
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI tutor. Use the context from the study guide to answer clearly.

Context:
{context}"""),
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

# Hint Node
def hint_node(state: TutorState):
    """Generates a hint instead of the full answer"""
    question = state["question"]
    docs = state["retrieved_docs"]

    print("[Hint Node] Generating Hint...")

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a tutor giving hints, NOT full answers.

Context:
{context}

Give a gentle hint that guides the student to think. Don't reveal the full answer."""),
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
    
# Save memory node
def save_memory_node(state: TutorState):
    """Marks a conversation as saved"""

    print("[Save Memory Node] Conversation Saved!")
    return {}


# Building the graph
def decide_next_step(state: TutorState):
    """Decides whether to give a hint or save to memory"""
    feedback = state.get("user_feedback", "")

    if feedback == "hint":
        print("[Router] User wants hint -> going to Hint Node")
        return "hint"
    else:
        print("[Router] Saving and ending -> going to Save Memory")
        return "save"
    
workflow = StateGraph(TutorState)

workflow.add_node("retriever", retriever_node)
workflow.add_node("llm", llm_node)
workflow.add_node("hint", hint_node)
workflow.add_node("save", save_memory_node)

workflow.set_entry_point("retriever")

workflow.add_edge("retriever", "llm")
workflow.add_conditional_edges(
    "llm",
    decide_next_step,
    {
        "hint": "hint",
        "save": "save"
    }
)

workflow.add_edge("hint", "save")

workflow.add_edge("save", END)

app = workflow.compile()


# Main Loop


print("\n🎓 Welcome to your AI Tutor!")
print("Ask questions about your study guide.")
print("After each answer, type 'hint' for a hint, or press Enter to continue.")
print("Type 'exit' to quit.\n")

chat_history = []

while True:
    query = input("You: ")

    if query.lower() in ["exit", "quit"]:
        print("Goodbye! Happy Studying!")
        break

    result = app.invoke({
        "question": query,
        "chat_history": chat_history,
        "retrieved_docs": [],
        "answer": "",
        "user_feedback": ""
    })

    print(f"\n AI Tutor:  {result['answer']} \n")

    chat_history = result["chat_history"]

    feedback = input("Type 'hint' for a hint, or press Enter to continue: ")

    if feedback.lower() == "hint":
        result = app.invoke({
            "question": query,
            "chat_history": chat_history[:-2],
            "retrieved_docs": result["retrieved_docs"],
            "answer": "",
            "user_feedback": "hint"
        })

        print(f"\n Hint: {result['answer']}")

        chat_history = result["chat_history"]

