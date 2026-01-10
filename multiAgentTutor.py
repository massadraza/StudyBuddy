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

Context from study guide:
{context}"""),
        ("human", "{question}")
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

workflow = StateGraph(TutorState)
workflow.add_node("retriever", retriever_agent)
workflow.add_node("tutor", tutor_agent)
workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "tutor")
workflow.add_edge("tutor", END)
app = workflow.compile()

chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    result = app.invoke({
        "question": query,
        "chat_history": chat_history,
        "retrieved_docs": [],
        "mode": "qa"
    })

    print(f"\n Tutor: {result['answer']}\n")
    chat_history = result["chat_history"]

